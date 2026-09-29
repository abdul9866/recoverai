import click
from semantic_search.index import fused_search

@click.command()
@click.argument("query")
@click.option("--k", default=10, help="Number of top search hits to retrieve")
@click.option("--alpha", default=0.6, help="Vector similarity weight")
@click.option("--beta", default=0.25, help="Recovery confidence weight")
@click.option("--gamma", default=0.15, help="Completeness fraction weight")
def search(query, k, alpha, beta, gamma):
    """Executes RecoverAI CARP Fused Semantic Search over recovered artifacts."""
    hits = fused_search(query, k=k, alpha=alpha, beta=beta, gamma=gamma)
    click.echo(f"\n--- RecoverAI CARP Fused Search Results for '{query}' ---")
    if not hits:
        click.echo("No matching artifacts found.")
        return

    for rank, r in enumerate(hits, 1):
        click.echo(
            f"[{rank}] Fused Score: {r['fused_score']:.4f} | Path: {r['path']}\n"
            f"    -> Similarity: {r['similarity']:.4f} | Recovery Conf: {r['recovery_confidence']:.4f} | Completeness: {r['completeness_fraction']:.4f}"
        )

if __name__ == "__main__":
    search()
