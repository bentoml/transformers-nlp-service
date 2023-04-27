from __future__ import annotations

import pytest
import typing as t
import bentoml
from bentoml.testing.utils import async_request
from bentoml._internal.utils import LazyLoader

if t.TYPE_CHECKING:
    from grpc_health.v1 import health_pb2 as pb_health

    P = t.TypeVar("P")
    Generator = t.Generator[P, None, None]
else:
    pb_health = LazyLoader("pb_health", globals(), "grpc_health.v1.health_pb2")

TEXT = """\
The three words that best describe Hunter Schafer's Vanity Fair Oscars party look? Less is more.
Dressed in a bias-cut white silk skirt, a single ivory-colored feather and — crucially — nothing else, Schafer was bound to raise a few eyebrows. Google searches for the actor and model skyrocketed on Sunday night as her look hit social media. On Twitter, pictures of Schafer immediately received tens of thousands of likes, while her own Instagram post has now been liked more than 2 million times.
Look of the Week: Zendaya steals the show at Louis Vuitton in head-to-toe tiger print
But more than just creating a headline-grabbing moment, Schafer's ensemble was clearly considered. Fresh off the Fall-Winter 2023 runway, the look debuted earlier this month at fashion house Ann Demeulemeester's show in Paris. It was designed by Ludovic de Saint Sernin, the label's creative director since December.
Celebrity fashion works best when there's a story behind a look. For example, the plausible Edie Sedgwick reference in Kendall Jenner's Bottega Veneta tights, or Paul Mescal winking at traditional masculinity in a plain white tank top.
For his first Ann Demeulemeester collection, De Saint Sernin was inspired by "fashion-making as an authentic act of self-involvement." It was a love letter — almost literally — to the Belgian label's founder, with imagery of "authorship and autobiography" baked into the clothes (Sernin called his feather bandeaus "quills" in the show notes).
Hunter Schafer's barely-there Oscars after party look was more poetic than it first seemed.
These ideas of self-expression, self-love and self-definition took on new meaning when worn by Schafer. As a trans woman whose ascent to fame was inextricably linked to her gender identity — her big break was playing trans teenager Jules in HBO's "Euphoria" — Schafer's body is subjected to constant scrutiny online. The comment sections on her Instagram posts often descend into open forums, where users feel entitled (and seemingly compelled) to ask intimate questions about the trans experience or challenge Schafer's womanhood.
Fittingly, there is a long lineage of gender-defying sentiments stitched into Schafer's outfit. Founded in 1985 by Ann Demeulemeester and her husband Patrick Robyn, the brand boasts a long legacy of gender-non-conforming fashion.
"I was interested in the tension between masculine and feminine, but also the tension between masculine and feminine within one person," Demeulemeester told Vogue ahead of a retrospective exhibition of her work in Florence, Italy, last year. "That is what makes every person really interesting to me because everybody is unique."
In his latest co-ed collection, De Saint Sernin — who is renowned in the industry for his eponymous, gender-fluid label — brought his androgynous world view to Ann Demeulemeester with fitted, romantic menswear silhouettes and sensual fabrics for all (think skin-tight mesh tops, leather, and open shirts made from a translucent organza material).
Celebrity stylist Law Roach on dressing Zendaya and 'faking it 'till you make it'
A quill strapped across her chest, Schafer let us know she is still writing her narrative — and defining herself on her own terms. There's an entire story contained in those two garments. As De Saint Sernin said in the show notes: "Thirty-six looks, each one a heartfelt sentence."
The powerful ensemble may become one of Law Roach's last celebrity styling credits. Roach announced over social media on Tuesday that he would be retiring from the industry after 14 years of creating conversation-driving looks for the likes of Zendaya, Bella Hadid, Anya Taylor-Joy, Ariana Grande and Megan Thee Stallion."""

CATEGORIES = [
    "world",
    "politics",
    "technology",
    "defence",
    "entertainment",
    "education",
    "healthcare",
    "parliament",
    "economy",
    "infrastructure",
    "business",
    "sport",
    "legal",
]


@pytest.mark.asyncio
@pytest.mark.skip_server_type("grpc")
async def test_api_server_meta_http(host: str) -> None:
    await async_request("GET", f"http://{host}", assert_status=200)
    await async_request("GET", f"http://{host}/healthz", assert_status=200)
    await async_request("GET", f"http://{host}/livez", assert_status=200)
    await async_request("GET", f"http://{host}/docs.json", assert_status=200)
    status, _, body = await async_request("GET", f"http://{host}/metrics")
    assert status == 200 and body


@pytest.mark.asyncio
@pytest.mark.skip_server_type("grpc")
async def test_inference_http(host: str):
    client = bentoml.client.Client.from_url(host, kind="http")
    resp = await client.async_health()
    assert resp.status == 200

    res = await client.async_summarize(TEXT)
    assert isinstance(res, str)

    res = await client.async_categorize({"text": TEXT, "categories": CATEGORIES})
    assert isinstance(res, dict) and res["entertainment"] > 0.5


@pytest.mark.asyncio
@pytest.mark.skip_server_type("http")
async def test_inference_grpc(host: str):
    client = bentoml.client.Client.from_url(host, kind="grpc")
    res = await client.health("bentoml.grpc.v1.BentoService", timeout=90)
    assert res.status == pb_health.HealthCheckResponse.SERVING

    res = await client.async_call("summarize", TEXT)
    assert res.text and isinstance(res.text.value, str)

    res = await client.async_call(
        "categorize", {"text": TEXT, "categories": CATEGORIES}
    )
    assert res.json and res.json.struct_value.fields["entertainment"].number_value > 0.5
