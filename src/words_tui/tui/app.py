import datetime

from textual.app import App, ComposeResult
from textual.widgets import Footer, Static

from words_tui.tui.db import Post
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


def get_sidebar_text(posts: list[Post]) -> str:
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
        self.posts: list[Post] = Post.select().order_by(Post.created_date.desc()).limit(10)
        todays_post: list[Post] = [post for post in self.posts if post.created_date.date() == datetime.date.today()]
        if todays_post:
            self.todays_post = todays_post[0]
        else:
            self.todays_post = Post.create(content="_")

        self.editor = TextEditor(id="editor")
        self.editor.show_line_numbers = False
        self.editor.load_text(self.todays_post.content)

    def on_text_editor_changed(self, _: TextEditor.Changed) -> None:
        self.update_word_count()

    def update_word_count(self) -> None:
        text_editor = self.query_one(TextEditor)
        sidebar = self.query_one("#sidebar")

        text = "\n".join(text_editor.document_lines)
        self.todays_post.content = text
        self.todays_post.save()

        text_editor.load_text(text)

        posts = Post.select().order_by(Post.created_date.desc()).limit(10)

        sidebar.update(get_sidebar_text(posts))

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Static(get_sidebar_text(self.posts), id="sidebar")
        yield self.editor
        yield Footer()


if __name__ == "__main__":
    app = WordsTui()
    app.run()
