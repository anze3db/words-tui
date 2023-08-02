import datetime
from pathlib import Path

from peewee import (
    DateTimeField,
    Model,
    SqliteDatabase,
    TextField,
)
from textual.app import App, ComposeResult
from textual.widgets import Footer, Static

from words_tui.tui.text_editor import TextEditor

db = SqliteDatabase(Path.home() / ".write-tui.db")
db.connect()


class BaseModel(Model):
    class Meta:
        database = db


class Post(BaseModel):
    content = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)


db.create_tables([Post])
posts = Post.select().order_by(Post.created_date.desc()).limit(10)
todays_post = [post for post in posts if post.created_date.date() == datetime.date.today()]
if not todays_post:
    todays_post = Post.create(content="_")
else:
    todays_post = todays_post[0]


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

    def on_mount(self) -> None:
        self.posts = Post.select().order_by(Post.created_date.desc()).limit(10)

    def on_text_editor_changed(self, event: TextEditor.Changed) -> None:
        self.update_word_count()

    def update_word_count(self) -> None:
        text_editor = self.query_one(TextEditor)
        sidebar = self.query_one("#sidebar")

        text = "\n".join(text_editor.document_lines)
        todays_post.content = text
        todays_post.save()

        text_editor.load_text(text)

        posts = Post.select().order_by(Post.created_date.desc()).limit(10)

        sidebar.update(get_sidebar_text(posts))

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        editor = TextEditor(id="editor")
        posts = Post.select().order_by(Post.created_date.desc()).limit(10)
        editor.show_line_numbers = False
        editor.load_text(todays_post.content)

        yield Static(get_sidebar_text(posts), id="sidebar")
        yield editor
        yield Footer()


if __name__ == "__main__":
    app = WordsTui()
    app.run()
