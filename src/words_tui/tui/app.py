import datetime

from textual.app import App, ComposeResult
from textual.widgets import Footer, Static

from words_tui.tui.db import Post, get_posts
from words_tui.tui.text_editor import TextEditor


def get_post_icon(post: Post) -> str:
    if len(post.content.split()) > 300:
        return "✅"
    elif post.created_date.date() == datetime.date.today():
        return "📝"
    return "❌"


def get_post_summary(post: Post) -> str:
    return " ".join(
        map(
            str,
            [
                get_post_icon(post),
                post.created_date.strftime("%Y-%m-%d"),
                f"{len(post.content.split()):5}/300",
            ],
        )
    )


def get_sidebar_text() -> str:
    posts = get_posts()
    return "[bold] # Date      Words/Goal[/bold]\n" + "\n".join(map(get_post_summary, posts))


class WordsTui(App):
    """A Textual app for writing."""

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
    ]

    CSS_PATH = "app.css"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # TODO: Find a better place for this
        self.posts = get_posts()

        if not self.posts:
            # When we first initialize the app there are no posts in the database, so create the first one:
            self.posts.insert(0, Post.create(content="", created_date=datetime.datetime.now()))
        else:
            latest_post = self.posts[0]
            missing_days = (datetime.date.today() - latest_post.created_date.date()).days
            start_date = latest_post.created_date.replace(hour=0, minute=0, second=0, microsecond=0)

            for day in range(missing_days):
                self.posts.insert(0, Post.create(content="", created_date=start_date + datetime.timedelta(days=day + 1)))

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

        sidebar.update(get_sidebar_text())

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Static(get_sidebar_text(), id="sidebar")
        yield self.editor
        yield Footer()


if __name__ == "__main__":
    app = WordsTui()
    app.run()
