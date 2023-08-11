import datetime

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.validation import Number
from textual.widgets import Footer, Input, Label, Static

from words_tui.tui.db import Post, get_posts, get_settings
from words_tui.tui.text_editor import TextEditor


def get_post_icon(post: Post, words_per_day: str) -> str:
    if len(post.content.split()) >= int(words_per_day):
        return "✅"
    elif post.created_date.date() == datetime.date.today():
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
            self.posts.insert(0, Post.create(content="", created_date=datetime.datetime.now()))
        else:
            latest_post = self.posts[0]
            missing_days = (datetime.date.today() - latest_post.created_date.date()).days
            start_date = latest_post.created_date.replace(hour=0, minute=0, second=0, microsecond=0)

            for day in range(missing_days):
                self.posts.insert(
                    0, Post.create(content="", created_date=start_date + datetime.timedelta(days=day + 1))
                )

        current_post = [post for post in self.posts if post.created_date.date() == datetime.date.today()]
        self.current_post: Post = current_post[0]

        self.editor = TextEditor(id="editor")
        self.editor.show_line_numbers = False
        self.editor.load_text(self.current_post.content)

    def on_text_editor_changed(self, _: TextEditor.Changed) -> None:
        self.update_word_count()

    def update_word_count(self) -> None:
        text_editor = self.query_one(TextEditor)
        sidebar = self.query_one("#sidebar")

        text = "\n".join(text_editor.document_lines)
        self.current_post.content = text
        self.current_post.save()

        sidebar.update(get_sidebar_text(self.words_per_day.value))

    def action_open_settings(self) -> None:
        def after_quit(words_per_day) -> None:
            self.editor.focus()
            self.words_per_day = words_per_day
            self.update_word_count()

        self.push_screen(SettingsScreen(), after_quit)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Static(get_sidebar_text(self.words_per_day.value), id="sidebar")
        yield self.editor
        yield Footer()


if __name__ == "__main__":
    app = WordsTui()
    app.run()
