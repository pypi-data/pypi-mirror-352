from pprint import pformat
import click
from masscode import MasscodeApi, MasscodeDBFile, Query
from masscode.core.discovery import get_dbpath
from masscode.model.query import TagQuery, SnippetQuery, FolderQuery


@click.group(invoke_without_command=True)
# api or file
@click.option("--mode", type=click.Choice(["api", "file"]), default="api")
@click.option("--path", type=click.Path(exists=True), default=None)
@click.pass_context
def cli(ctx, mode, path):
    if mode == "api":
        ctx.obj = MasscodeApi()
        ctx.obj.start_masscode()
    elif mode == "file":
        path = path or get_dbpath()
        ctx.obj = MasscodeDBFile(path)
    else:
        raise click.UsageError("Invalid mode")


@cli.command()
@click.option("-l", "--list", is_flag=True)
@click.option("-c", "--count", type=int, default=-1)
@click.pass_obj
def folders(obj, list, count):
    for folder in obj.folders:
        if list:
            click.echo(folder.name)
        else:
            click.echo(pformat(folder))


@cli.command()
@click.option("-l", "--list", is_flag=True)
@click.option("-c", "--count", type=int, default=-1)
@click.pass_obj
def snippets(obj, list, count):
    for snippet in obj.snippets:
        if list:
            click.echo(snippet.name)
        else:
            click.echo(pformat(snippet))


@cli.command()
@click.option("-l", "--list", is_flag=True)
@click.option("-c", "--count", type=int, default=-1)
@click.pass_obj
def tags(obj, list, count):
    for tag in obj.tags:
        if list:
            click.echo(tag.name)
        else:
            click.echo(pformat(tag))


@cli.group()
def query():
    pass


@query.command()
@click.option("--name", "-n", type=str, default=None)
@click.option("--query", "-q", type=str, default=None)
@click.option("--created-at", "-c", type=int, default=None)
@click.option("--updated-at", "-u", type=int, default=None)
@click.pass_obj
def tag(obj, name, query, created_at, updated_at):
    tagquery: TagQuery = Query.tag(
        name=name, query=query, createdAt=created_at, updatedAt=updated_at
    )
    for tag in obj.query_tag(tagquery):
        click.echo(pformat(tag))


@query.command()
@click.option("--name", "-n", type=str, default=None)
@click.option("--default-language", "-l", type=str, default=None)
@click.option("--parent", "-p", type=str, default=None)
@click.option("--is-open", "-o", is_flag=True, default=None)
@click.option("--is-system", "-s", is_flag=True, default=None)
@click.option("--created-at", "-c", type=int, default=None)
@click.option("--updated-at", "-u", type=int, default=None)
@click.option("--query", "-q", type=str, default=None, help="Python expression to evaluate on folder, e.g. '(x[\"name\"].startswith(\"py\") and x[\"isOpen\"])'")
@click.pass_obj
def folder(obj, name, default_language, parent, is_open, is_system, created_at, updated_at, query):
    folderquery: FolderQuery = Query.folder(
        name=name,
        defaultLanguage=default_language,
        parent=parent,  # Will be converted to parentId if it's a folder name
        isOpen=is_open,
        isSystem=is_system,
        createdAt=created_at,
        updatedAt=updated_at,
        query=query
    )
    for folder in obj.query_folder(folderquery):
        click.echo(pformat(folder))


@query.command()
@click.option("--name", "-n", type=str, default=None)
@click.option("--folder", "-f", type=str, default=None, help="Folder name or ID")
@click.option("--is-deleted", "-d", is_flag=True, default=None)
@click.option("--is-favorites", "-v", is_flag=True, default=None)
@click.option("--tags", "-t", multiple=True, help="Tag names or IDs (can be specified multiple times)")
@click.option("--created-at", "-C", type=int, default=None)
@click.option("--updated-at", "-u", type=int, default=None)
@click.option("--query", "-q", type=str, default=None, help="Python expression to evaluate on snippet, e.g. '(x[\"name\"].startswith(\"py\") and len(x[\"content\"]) > 1)'")
@click.pass_obj
def snippet(obj, name, folder, is_deleted, is_favorites, tags, created_at, updated_at, query):

    tagquery : TagQuery = Query.tag(query=f"x['name'] in {tags} or x['id'] in {tags}")
    tags = obj.query_tag(tagquery)    
    tags = [tag["id"] for tag in tags]


    snippetquery: SnippetQuery = Query.snippet(
        name=name,
        folder=folder,  
        isDeleted=is_deleted,
        isFavorites=is_favorites,
        tags=tags,  
        createdAt=created_at,
        updatedAt=updated_at,
        query=query
    )
    for snippet in obj.query_snippet(snippetquery):
        click.echo(pformat(snippet))


if __name__ == "__main__":
    cli()
