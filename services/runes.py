"""Elder Futhark: 24 rune, nomi storici. I testi sono il dataset, non la UI."""

from __future__ import annotations

import random
from typing import Any

ELDER_FUTHARK: tuple[dict[str, Any], ...] = (
    {
        "id": "fehu",
        "name": "Fehu",
        "glyph": "ᚠ",
        "phonetic": "F",
        "reversible": True,
        "upright": "Bestame, ricchezza mobile, inizio fertile. Qualcosa di concreto puo entrare o circolare.",
        "reversed": "Perdita, spreco, attaccamento a cio che non si ferma. Controllare dove esce l'energia.",
    },
    {
        "id": "uruz",
        "name": "Uruz",
        "glyph": "ᚢ",
        "phonetic": "U",
        "reversible": True,
        "upright": "Forza selvatica del bue, vitalita, prova fisica. Una spinta grezza chiede di essere guidata.",
        "reversed": "Forza dispersa, debolezza, occasione mancata. Recuperare il corpo prima della strategia.",
    },
    {
        "id": "thurisaz",
        "name": "Thurisaz",
        "glyph": "ᚦ",
        "phonetic": "TH",
        "reversible": True,
        "upright": "Il gigante, la spina, la soglia pericolosa. Difesa e rottura: agire con precisione, non con rabbia.",
        "reversed": "Impulso cieco, conflitto inutile. La spina si rivolta contro chi la impugna di fretta.",
    },
    {
        "id": "ansuz",
        "name": "Ansuz",
        "glyph": "ᚨ",
        "phonetic": "A",
        "reversible": True,
        "upright": "Bocca degli dei, parola, segnale. Un messaggio, un consiglio, una voce da ascoltare.",
        "reversed": "Parola storta, rumore, consiglio inaffidabile. Verificare la fonte prima di credere.",
    },
    {
        "id": "raidho",
        "name": "Raidho",
        "glyph": "ᚱ",
        "phonetic": "R",
        "reversible": True,
        "upright": "Il viaggio, il ritmo, la strada giusta. Muoversi con ordine, non restare fermi per paura.",
        "reversed": "Viaggio interrotto, ritardo, direzione confusa. Rivedere il percorso prima di accelerare.",
    },
    {
        "id": "kenaz",
        "name": "Kenaz",
        "glyph": "ᚲ",
        "phonetic": "K",
        "reversible": True,
        "upright": "La torcia, il sapere che illumina. Una conoscenza o un mestiere puo aprire la via.",
        "reversed": "Luce che si spegne, falsa chiarezza. Non forzare una rivelazione che non e pronta.",
    },
    {
        "id": "gebo",
        "name": "Gebo",
        "glyph": "ᚷ",
        "phonetic": "G",
        "reversible": False,
        "upright": "Il dono, lo scambio, l'alleanza. Dare e ricevere in equilibrio, senza debito nascosto.",
        "reversed": "",
    },
    {
        "id": "wunjo",
        "name": "Wunjo",
        "glyph": "ᚹ",
        "phonetic": "W",
        "reversible": True,
        "upright": "Gioia, armonia, appartenenza. Un momento in cui le parti stanno insieme senza sforzo.",
        "reversed": "Gioia rimandata, disaccordo, festa interrotta. Non fingere un'armonia che non c'e.",
    },
    {
        "id": "hagalaz",
        "name": "Hagalaz",
        "glyph": "ᚺ",
        "phonetic": "H",
        "reversible": False,
        "upright": "La grandine: rottura che viene dal cielo. Un evento esterno rimescola, poi lascia terra nuova.",
        "reversed": "",
    },
    {
        "id": "nauthiz",
        "name": "Nauthiz",
        "glyph": "ᚾ",
        "phonetic": "N",
        "reversible": True,
        "upright": "Il bisogno, la costrizione che insegna. Tempi stretti: pazienza e mestiere, non fuga.",
        "reversed": "Resistenza inutile, bisogno negato. Nominare cio che manca invece di ignorarlo.",
    },
    {
        "id": "isa",
        "name": "Isa",
        "glyph": "ᛁ",
        "phonetic": "I",
        "reversible": False,
        "upright": "Il ghiaccio, la pausa, la concentrazione ferma. Niente si muove: osservare, non spingere.",
        "reversed": "",
    },
    {
        "id": "jera",
        "name": "Jera",
        "glyph": "ᛃ",
        "phonetic": "J",
        "reversible": False,
        "upright": "L'anno, il raccolto, il ciclo. Cio che e stato seminato torna, nei tempi della stagione.",
        "reversed": "",
    },
    {
        "id": "eihwaz",
        "name": "Eihwaz",
        "glyph": "ᛇ",
        "phonetic": "EI",
        "reversible": False,
        "upright": "Il tasso, asse tra mondi. Resistenza, transizione, protezione nel passaggio.",
        "reversed": "",
    },
    {
        "id": "perthro",
        "name": "Perthro",
        "glyph": "ᛈ",
        "phonetic": "P",
        "reversible": True,
        "upright": "Il dado, il mistero, cio che ancora non si rivela. Lasciare spazio al caso e al non saputo.",
        "reversed": "Segreto che stona, aspettativa delusa. Non pretendere di leggere cio che e ancora chiuso.",
    },
    {
        "id": "algiz",
        "name": "Algiz",
        "glyph": "ᛉ",
        "phonetic": "Z",
        "reversible": True,
        "upright": "L'alce, la protezione, la mano alzata. Un confine sano, un aiuto, una guardia.",
        "reversed": "Sguarniti, allarme ignorato. Ripristinare i limiti prima di avanzare.",
    },
    {
        "id": "sowilo",
        "name": "Sowilo",
        "glyph": "ᛊ",
        "phonetic": "S",
        "reversible": False,
        "upright": "Il sole, la vittoria chiara, la direzione. Energia che mostra la strada senza ombra.",
        "reversed": "",
    },
    {
        "id": "tiwaz",
        "name": "Tiwaz",
        "glyph": "ᛏ",
        "phonetic": "T",
        "reversible": True,
        "upright": "Tyr, giustizia, coraggio del sacrificio. Agire per cio che e retto, anche se costa.",
        "reversed": "Ingiustizia, causa persa, orgoglio ferito. Verificare se la battaglia e ancora la tua.",
    },
    {
        "id": "berkano",
        "name": "Berkano",
        "glyph": "ᛒ",
        "phonetic": "B",
        "reversible": True,
        "upright": "La betulla, nascita, cura, crescita lenta. Qualcosa di nuovo va protetto, non esposto.",
        "reversed": "Crescita bloccata, cura mancata. Un inizio ha bisogno di nido, non di vetrina.",
    },
    {
        "id": "ehwaz",
        "name": "Ehwaz",
        "glyph": "ᛖ",
        "phonetic": "E",
        "reversible": True,
        "upright": "Il cavallo, il movimento a due, la fiducia. Un partner, un mezzo, un avanzare insieme.",
        "reversed": "Sfiducia, passo falso, coppia che non tiene il ritmo. Riallineare prima di partire.",
    },
    {
        "id": "mannaz",
        "name": "Mannaz",
        "glyph": "ᛗ",
        "phonetic": "M",
        "reversible": True,
        "upright": "L'essere umano, la comunita, lo specchio. Vedere se stessi tra gli altri, senza isolarsi.",
        "reversed": "Isolamento, maschera, giudizio. Tornare a una relazione onesta con le persone.",
    },
    {
        "id": "laguz",
        "name": "Laguz",
        "glyph": "ᛚ",
        "phonetic": "L",
        "reversible": True,
        "upright": "L'acqua, l'intuito, il flusso. Seguire la corrente interiore invece di arginarla.",
        "reversed": "Paura dell'acqua, emozione repressa. Cio che non si sente torna come marea.",
    },
    {
        "id": "ingwaz",
        "name": "Ingwaz",
        "glyph": "ᛜ",
        "phonetic": "NG",
        "reversible": False,
        "upright": "Ing, il seme chiuso, gestazione. Il lavoro interno e quasi maturo: non aprirlo troppo presto.",
        "reversed": "",
    },
    {
        "id": "dagaz",
        "name": "Dagaz",
        "glyph": "ᛞ",
        "phonetic": "D",
        "reversible": False,
        "upright": "Il giorno, lo spartiacque, il passaggio dalla notte. Un cambio di fase e gia in corso.",
        "reversed": "",
    },
    {
        "id": "othala",
        "name": "Othala",
        "glyph": "ᛟ",
        "phonetic": "O",
        "reversible": True,
        "upright": "L'eredita, la casa, cio che resta. Radici, beni, tradizione da abitare senza chiudersi.",
        "reversed": "Eredita pesante, casa instabile, attaccamento al passato. Distinguere radice e catena.",
    },
)


def get_rune(rune_id: str) -> dict[str, Any] | None:
    for item in ELDER_FUTHARK:
        if item["id"] == rune_id:
            return item
    return None


def draw_runes(count: int) -> list[dict[str, str]]:
    count = 1 if count != 3 else 3
    pool = list(ELDER_FUTHARK)
    random.shuffle(pool)
    drawn: list[dict[str, str]] = []
    for item in pool[:count]:
        reversed_rune = bool(item["reversible"]) and random.choice((False, True))
        meaning = str(item["reversed"] if reversed_rune else item["upright"])
        drawn.append(
            {
                "id": str(item["id"]),
                "name": str(item["name"]),
                "glyph": str(item["glyph"]),
                "phonetic": str(item["phonetic"]),
                "orientation": "reversed" if reversed_rune else "upright",
                "meaning": meaning,
            }
        )
    return drawn


def synthesize_runes(question: str, drawn: list[dict[str, str]]) -> str:
    if not drawn:
        return ""
    if len(drawn) == 1:
        piece = drawn[0]
        orient = "capovolta" if piece["orientation"] == "reversed" else "diritta"
        base = f"{piece['name']} ({orient}): {piece['meaning']}"
        if question:
            return f"Sulla domanda «{question}», {base}"
        return base
    labels = ("situazione", "ostacolo", "direzione")
    bits = []
    for idx, piece in enumerate(drawn[:3]):
        orient = "capovolta" if piece["orientation"] == "reversed" else "diritta"
        bits.append(f"{labels[idx]} — {piece['name']} {orient}: {piece['meaning']}")
    body = " ".join(bits)
    if question:
        return f"Domanda: «{question}». {body}"
    return body
