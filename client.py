from __future__ import annotations

import bentoml

SAMPLES = """
Fox News reached a last-second settlement with Dominion Voting Systems on Tuesday as the case raced toward opening statements, paying more than $787 million to end a colossal two-year legal battle that publicly shredded the right-wing network’s credibility.
Fox News’ $787.5 million settlement with Dominion Voting Systems is the largest publicly known defamation settlement in US history involving a media company.
The deal was announced hours after the jury was sworn in at the Delaware Superior Court. Rumors of a settlement swirled in the courthouse when, after a lunch break, the proceedings dramatically ground to a halt for nearly three hours with no explanation, while the parties apparently hammered out an accord.
“The parties have resolved their case,” Judge Eric Davis said, before dismissing the 12-member jury, crediting them with giving the parties an impetus to reach a settlement, effusively praising the lawyers from both sides, and gaveling out the so-called media “trial of the century” before it could even begin.
The groundbreaking settlement “represents vindication and accountability,” Dominion lawyer Justin Nelson said. “For our democracy to endure for another 250 years, and hopefully much longer, we must share a commitment to facts… Today represents a ringing endorsement for truth and for democracy.”
The right-wing network said in a statement that it “acknowledge[s] the Court’s rulings finding certain claims about Dominion to be false,” referring to Davis’ recent ruling that 20 Fox News broadcasts from late 2020 contained blatantly untrue assertions that Dominion rigged the presidential election. But Fox won’t have to admit on-air that it spread lies about Dominion, a Dominion representative told CNN.
The $787.5 million payout is roughly half of the $1.6 billion that Dominion initially sought, though it is nearly 10 times the company’s valuation from 2018, and roughly eight times its annual revenue in 2021, according to court filings.
The last-minute agreement means the closely watched case is over and won’t proceed to trial. By settling with Dominion, influential Fox News executives and prominent on-air personalities will be spared from testifying about their 2020 election coverage, which was filled with lies about voter fraud.
The witness list included Fox Corporation chairman Rupert Murdoch, his CEO son Lachlan Murdoch, and top Fox hosts like Sean Hannity and Tucker Carlson. Damning emails, texts, and deposition testimony made public during the case revealed that these figures, and many others at Fox, privately said in 2020 that the vote-rigging claims against Dominion were asinine. But the lies were spread on-air anyway.
Rupert Murdoch thought the election denialism was “really crazy,” even as Fox personalities peddled those same claims to millions of viewers. Carlson said he “passionately” hates Donald Trump, whose presidency was a “disaster.” Fox hosts, producers, fact-checkers, and senior executives privately said in the on-air claims of a stolen election were “kooky,” “dangerously reckless” and “mind-blowingly nuts.”
These revelations generated months of blistering headlines for Fox as the case moved toward trial. By settling now, Fox deprived Dominion a chance to further expose its dishonesty with a weeks-long trial.
“This settlement reflects Fox’s continued commitment to the highest journalistic standards,” Fox said in a statement Tuesday. “We are hopeful that our decision to resolve this dispute with Dominion amicably, instead of the acrimony of a divisive trial, allows the country to move forward from these issues.”
Fox News and Fox Corporation – its parent company, which was also a defendant – maintain they never defamed Dominion, and say the case was a meritless assault on First Amendment press freedoms.
"""

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


def call(host: str = "127.0.0.1") -> None:
    client = bentoml.client.Client.from_url(f"{host}:3000")

    print("Summarized text from the article:", client.summarize(SAMPLES))

    print(
        "Category of the article:",
        client.categorize({"text": SAMPLES, "categories": CATEGORIES}),
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")

    args = parser.parse_args()

    call(host=args.host)
