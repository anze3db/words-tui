import datetime as dt
import time

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.validation import Number
from textual.widgets import Footer, Input, Label, Static

from words_tui.tui.db import Post, PostStats, get_posts, get_settings
from words_tui.tui.text_editor import TextEditor


def get_post_icon(post: Post, words_per_day: str) -> str:
    if len(post.content.split()) >= int(words_per_day):
        return "✅"
    elif post.created_date.date() == dt.date.today():
        return "📝"
    return "❌"


def get_post_summary(post: Post, words_per_day: str) -> str:
    return " ".join(
        map(
            str,
            [
                get_post_icon(post, words_per_day),
                post.created_date.strftime("%Y-%m-%d"),
                f"{len(post.content.split()):5}/{words_per_day}",
            ],
        )
    )


def get_sidebar_text(words_per_day: str) -> str:
    posts = get_posts()
    return "[bold] # Date      Words/Goal[/bold]\n" + "\n".join(get_post_summary(post, words_per_day) for post in posts)


class SettingsScreen(ModalScreen):
    CSS_PATH = "settings.css"
    BINDINGS = [
        ("escape", "dismiss", "Back"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def action_dismiss(self) -> None:
        self.dismiss(get_settings())

    def compose(self) -> ComposeResult:
        words_per_day = get_settings()
        with Vertical(id="grid"):
            yield Label(
                "Settings",
                id="settings_label",
            )
            yield Label(
                "Number of words per day",
                id="per_day_label",
            )
            yield Input(
                words_per_day.value,
                id="per_day_input",
                validators=[
                    Number(minimum=1, maximum=9999),
                ],
            )
        yield Footer()

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        if not event.validation_result.is_valid:
            return

        words_per_day = get_settings()
        words_per_day.value = event.input.value
        words_per_day.save()


class WordsPerMinuteCounter:
    def __init__(self, post: Post, words_per_day: int):
        self.paused = True
        self.words_per_day = words_per_day
        self.last_char_written = 0

        self.post = post
        self.stats = post.stats.first()
        if not self.post.stats:
            self.stats = PostStats(post=self.post)

        self.total_words = self._get_num_words()

        self.words_written = self.stats.words_written
        self.words_deleted = self.stats.words_deleted
        self.pauses = self.stats.pauses
        self.time_writing = self.stats.time_writing

    def _get_num_words(self):
        return len(self.post.content.split())

    def type_character(self):
        if self.paused:
            self.last_char_written = time.monotonic()
            self.paused = False
        else:
            current_time = time.monotonic()
            self.time_writing += current_time - self.last_char_written
            self.last_char_written = current_time

        words = self._get_num_words()
        diff = words - self.total_words
        self.total_words += diff
        if diff > 0:
            self.words_written += diff
        if diff < 0:
            self.words_deleted += abs(diff)
        self.total_words = words

    def update_words(self):
        if self.paused:
            return
        since_last_char = time.monotonic() - self.last_char_written
        if since_last_char > 2:
            self.paused = True
            self.pauses += 1
            return

        checkpoint_index = str(int(self.time_writing) // 60)

        self.stats.per_minute[checkpoint_index] = {
            "words_written": self.words_written,
            "words_deleted": self.words_deleted,
            "pauses": self.pauses,
        }
        self.stats.words_written = self.words_written
        self.stats.words_deleted = self.words_deleted
        self.stats.pauses = self.pauses
        self.stats.time_writing = self.time_writing

        if self.stats.writing_time_until_goal is None and self.words_written - self.words_deleted >= int(
            self.words_per_day.value
        ):
            self.stats.writing_time_until_goal = self.time_writing

        self.stats.save()

    def get_wpm(self) -> str:
        if self.last_char_written == 0:
            return "Not started"
        if self.paused or not self.stats:
            return "Paused"
        if self.time_writing < 10:
            return "~"

        return f"{self.words_written / self.time_writing * 60:.2f}"


class WordsTui(App):
    """A Textual app for writing."""

    BINDINGS = [("ctrl+c", "quit", "Quit"), ("ctrl+s", "open_settings", "Settings")]
    SCREENS = {"settings": SettingsScreen()}

    CSS_PATH = "app.css"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # TODO: Find a better place for this
        self.posts = get_posts()
        self.words_per_day = get_settings()

        if not self.posts:
            # When we first initialize the app there are no posts in the database, so create the first one:
            self.posts.insert(0, Post.create(content="", created_date=dt.datetime.now()))
        else:
            latest_post = self.posts[0]
            missing_days = (dt.date.today() - latest_post.created_date.date()).days
            start_date = latest_post.created_date.replace(hour=0, minute=0, second=0, microsecond=0)

            for day in range(missing_days):
                self.posts.insert(0, Post.create(content="", created_date=start_date + dt.timedelta(days=day + 1)))

        current_post = [post for post in self.posts if post.created_date.date() == dt.date.today()]
        self.current_post: Post = current_post[0]

        self.words_per_minute = WordsPerMinuteCounter(self.current_post, words_per_day=self.words_per_day)
        self.editor = TextEditor(id="editor")
        self.editor.show_line_numbers = False
        self.editor.load_text(self.current_post.content)

    def on_mount(self) -> None:
        self.set_interval(1, self.update_wpm)

    def update_wpm(self) -> None:
        self.words_per_minute.update_words()
        try:
            wpm = self.query_one("#wpm")
        except NoMatches:
            return
        wpm.update(f"WPM: {self.words_per_minute.get_wpm()}")

    def on_text_editor_changed(self, _: TextEditor.Changed) -> None:
        self.update_word_count()

    def update_word_count(self) -> None:
        sidebar = self.query_one("#sidebar")
        text_editor = self.query_one(TextEditor)

        text = "\n".join(text_editor.document_lines)
        self.current_post.content = text
        self.current_post.save()

        self.words_per_minute.type_character()
        sidebar.update(get_sidebar_text(self.words_per_day.value))

    def action_open_settings(self) -> None:
        def after_quit(words_per_day) -> None:
            self.editor.focus()
            self.words_per_day = words_per_day
            self.words_per_minute.words_per_day = words_per_day
            self.update_word_count()

        self.push_screen(SettingsScreen(), after_quit)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Static(get_sidebar_text(self.words_per_day.value), id="sidebar")
        yield Static(
            f"WPM: Not started",
            id="wpm",
        )
        yield self.editor
        yield Footer()


if __name__ == "__main__":
    app = WordsTui()
    app.run()
