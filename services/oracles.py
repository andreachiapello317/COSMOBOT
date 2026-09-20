"""Mazzi originali COSMOBOT e oracoli rapidi. Testi del dataset, non previsioni."""

from __future__ import annotations

import random
from typing import Any

from services.lenormand import synthesize_lenormand
from services.runes import draw_runes

# ---------------------------------------------------------------------------
# Archetipi — 48 carte proprietarie
# ---------------------------------------------------------------------------

ARCHETYPES: tuple[dict[str, str], ...] = (
    {"id": "warrior", "emoji": "🔥", "it": "Il Guerriero", "keys": "coraggio · confine · azione", "light": "Difendi ciò che conta senza cercare il nemico.", "shadow": "Combatti per non sentire.", "question": "Cosa merita davvero la tua forza, oggi?", "message": "La spada serve al recinto, non alla guerra permanente."},
    {"id": "traveler", "emoji": "🌊", "it": "Il Viaggiatore", "keys": "soglia · movimento · curiosità", "light": "Parti perché qualcosa chiama, non perché fuggi.", "shadow": "Cammini per non abitare.", "question": "Quale passo piccolo sarebbe già un viaggio?", "message": "La strada inizia dove smetti di preparare lo zaino."},
    {"id": "shadow", "emoji": "🌙", "it": "L'Ombra", "keys": "rimosso · paura · tesoro", "light": "Ciò che eviti contiene una parte di te.", "shadow": "Proietti sull'altro il pezzo che non vuoi.", "question": "Cosa stai evitando di vedere chiaramente?", "message": "L'ombra non è il nemico: è la stanza senza luce."},
    {"id": "change", "emoji": "🦋", "it": "La Trasformazione", "keys": "muta · crisalide · dopo", "light": "Qualcosa di te sta cambiando forma.", "shadow": "Resisti e chiami resistenza 'fedeltà'.", "question": "Cosa deve morire perché tu possa continuare?", "message": "Non torni bruco. Puoi solo diventare altro."},
    {"id": "key", "emoji": "🗝️", "it": "La Chiave", "keys": "accesso · soluzione · sì", "light": "Hai già il gesto che apre.", "shadow": "Cerchi chiavi nuove per porte che non vuoi aprire.", "question": "Cosa può essere aperto, se smetti di girare a vuoto?", "message": "La chiave è un atto, non un oggetto da collezionare."},
    {"id": "mirror", "emoji": "🪞", "it": "Lo Specchio", "keys": "riflesso · verità · volto", "light": "Ti vedi senza trucco, e tieni lo sguardo.", "shadow": "Rompi lo specchio e dai la colpa al vetro.", "question": "Cosa riflette questa situazione di te?", "message": "Non è l'altro: è il tuo volto, in un'altra luce."},
    {"id": "guardian", "emoji": "🛡️", "it": "Il Guardiano", "keys": "soglia · protezione · no", "light": "Sai dire no senza chiudere il mondo.", "shadow": "Custodisci anche ciò che andrebbe lasciato.", "question": "Cosa stai proteggendo, e da chi?", "message": "Un buon guardiano sa anche aprire."},
    {"id": "dreamer", "emoji": "☁️", "it": "Il Sognatore", "keys": "visione · notte · possibile", "light": "Vedi oltre il giorno utile.", "shadow": "Sogni per non scegliere.", "question": "Quale immagine vuoi tenere quando ti svegli?", "message": "Il sogno chiede un piccolo atto diurno."},
    {"id": "healer", "emoji": "🌿", "it": "Il Guaritore", "keys": "cura · ascolto · rammendo", "light": "Tieni insieme ciò che si è spaccato.", "shadow": "Curare gli altri per non toccare te.", "question": "Dove hai bisogno di una cura minuta, non eroica?", "message": "Guarire è spesso togliere pressione, non aggiungere rimedi."},
    {"id": "fool", "emoji": "🃏", "it": "Il Folle", "keys": "inizio · rischio · leggerezza", "light": "Parti senza avere tutte le mappe.", "shadow": "Chiami libertà la fuga dai conti.", "question": "Quale primo passo sciocco sarebbe anche vero?", "message": "Il folle non è stupido: è disponibile."},
    {"id": "king", "emoji": "👑", "it": "Il Re", "keys": "ordine · responsabilità · territorio", "light": "Prendi il posto che ti spetta, senza teatro.", "shadow": "Comandi per paura del vuoto.", "question": "Di che regno sei davvero responsabile?", "message": "Il trono è un lavoro, non un costume."},
    {"id": "queen", "emoji": "🌹", "it": "La Regina", "keys": "presenza · campo · dignità", "light": "Tieni lo spazio. Non rincorrere.", "shadow": "Controlli l'atmosfera invece di abitarla.", "question": "Dove puoi regnare senza alzare la voce?", "message": "La regalità è un clima, non un ordine."},
    {"id": "hermit", "emoji": "🏮", "it": "L'Eremita", "keys": "ritiro · lanterna · silenzio", "light": "Ti fai da parte per vedere.", "shadow": "Ti nascondi e chiami saggezza.", "question": "Di quale solitudine hai bisogno, e quale è solo isolamento?", "message": "La lanterna illumina un passo, non l'intera valle."},
    {"id": "lovers", "emoji": "💕", "it": "Gli Amanti", "keys": "scelta · legame · desiderio", "light": "Scegli con il corpo e con la voce.", "shadow": "Confondi fusione e amore.", "question": "Cosa stai scegliendo, e cosa stai solo subendo?", "message": "Amare è anche distinguere due persone."},
    {"id": "judge", "emoji": "⚖️", "it": "Il Giudice", "keys": "misura · verità · sentenza", "light": "Nomini le cose con il loro peso.", "shadow": "Condanni per sentirti pulito.", "question": "Quale giudizio puoi sospendere per ventiquattr'ore?", "message": "Giustizia non è vendetta con una toga."},
    {"id": "child", "emoji": "🧒", "it": "Il Bambino", "keys": "gioco · bisogno · inizio", "light": "Chiedi senza vergogna.", "shadow": "Fai il piccolo per non decidere.", "question": "Quale bisogno semplice non hai detto ad alta voce?", "message": "Il bambino in te non è un alibi: è un termometro."},
    {"id": "elder", "emoji": "🕯", "it": "L'Anziano", "keys": "tempo · memoria · consiglio", "light": "Porti ciò che hai già attraversato.", "shadow": "Usi il passato per vietare il presente.", "question": "Cosa sa di te chi è più vecchio di questa stagione?", "message": "L'esperienza è un dono, non un divieto."},
    {"id": "alchemist", "emoji": "⚗️", "it": "L'Alchimista", "keys": "trasmutare · opera · pazienza", "light": "Prendi il piombo e ne fai altro.", "shadow": "Manipoli per non accettare la materia.", "question": "Quale scarto tuo può diventare materiale?", "message": "L'opera nera viene prima dell'oro. Non saltarla."},
    {"id": "weaver", "emoji": "🧵", "it": "La Tessitrice", "keys": "trama · relazioni · tempo", "light": "Unisci fili senza affrettare il disegno.", "shadow": "Controlli ogni nodo e soffochi il tessuto.", "question": "Quale filo puoi lasciare andare senza strappare il resto?", "message": "Non sei l'unico telaio in questa stanza."},
    {"id": "hunter", "emoji": "🏹", "it": "Il Cacciatore", "keys": "mira · fame · inseguimento", "light": "Sai cosa vuoi e ti muovi pulito.", "shadow": "Insegui per non essere trovato.", "question": "Cosa stai cacciando, e cosa ti sta cacciando?", "message": "La preda giusta non richiede di svuotare la vita."},
    {"id": "oracle", "emoji": "🔮", "it": "L'Oracolo", "keys": "ascolto · segno · parola", "light": "Dici ciò che vedi, senza ricamare.", "shadow": "Parli in enigmi per non esporti.", "question": "Quale verità semplice stai complicando?", "message": "Un oracolo onesto sa anche dire: non so."},
    {"id": "bridge", "emoji": "🌉", "it": "Il Ponte", "keys": "passaggio · mediazione · rischio", "light": "Tieni due rive senza appartenere a una sola.", "shadow": "Resti in mezzo per non sbarcare.", "question": "Quale riva hai paura di toccare?", "message": "Il ponte esiste per essere attraversato."},
    {"id": "threshold", "emoji": "🚪", "it": "La Soglia", "keys": "prima · dopo · coraggio", "light": "Sei sul bordo. Un passo cambia stanza.", "shadow": "Abito la porta e la chiami casa.", "question": "Cosa c'è subito dopo questa porta?", "message": "Restare sulla soglia stanca più che entrare."},
    {"id": "seed", "emoji": "🌱", "it": "Il Seme", "keys": "potenziale · attesa · cura", "light": "Qualcosa è già iniziato, sotto terra.", "shadow": "Sotterri per non rischiare il germoglio.", "question": "Cosa stai piantando senza dirtelo?", "message": "Il seme non ha bisogno di applausi. Ha bisogno di terra."},
    {"id": "harvest", "emoji": "🌾", "it": "Il Raccolto", "keys": "frutto · resa · fine stagione", "light": "Prendi ciò che hai coltivato.", "shadow": "Lasci marcire per umiltà falsa.", "question": "Cosa è già maturo e non stai raccogliendo?", "message": "Raccogliere è un atto di rispetto, non di avidità."},
    {"id": "storm", "emoji": "⛈️", "it": "La Tempesta", "keys": "rottura · scarica · aria nuova", "light": "Il cielo si pulisce dopo il rumore.", "shadow": "Provochi tuoni per sentirti vivo.", "question": "Quale temporale sta passando, e quale lo stai chiamando?", "message": "Non tutto ciò che scuote è un nemico."},
    {"id": "hearth", "emoji": "🔥", "it": "Il Focolare", "keys": "calore · quotidiano · centro", "light": "Tieni viva una fiamma piccola e costante.", "shadow": "Bruci la casa per avere luce.", "question": "Dove puoi fare caldo senza incendiare?", "message": "Il sacro è spesso una pentola, non un altare."},
    {"id": "labyrinth", "emoji": "🌀", "it": "Il Labirinto", "keys": "perdita · centro · percorso", "light": "Ti perdi per trovare il mezzo.", "shadow": "Giri in tondo e chiami ricerca.", "question": "Stai camminando verso il centro o solo evitando l'uscita?", "message": "Nel labirinto si va avanti anche tornando."},
    {"id": "spring", "emoji": "⛲", "it": "La Fonte", "keys": "origine · sete · rinnovamento", "light": "Torni dove l'acqua è ancora pulita.", "shadow": "Bevi ovunque tranne che alla tua origine.", "question": "Di cosa hai sete, di preciso?", "message": "La fonte non insegue chi ha troppa fretta."},
    {"id": "mask", "emoji": "🎭", "it": "La Maschera", "keys": "ruolo · protezione · gioco", "light": "Sai quale volto serve in quale stanza.", "shadow": "Hai scordato il volto sotto.", "question": "Quale maschera puoi togliere stasera, anche per un'ora?", "message": "Una maschera utile si toglie. Una prigione no."},
    {"id": "voice", "emoji": "📣", "it": "La Voce", "keys": "parola · canto · dichiarazione", "light": "Dici la cosa vera, alla volume giusta.", "shadow": "Urli o taci: niente in mezzo.", "question": "Quale frase non hai ancora detto alla persona giusta?", "message": "La voce è un muscolo. Si allena in frasi corte."},
    {"id": "silence", "emoji": "🤫", "it": "Il Silenzio", "keys": "pausa · ascolto · vuoto", "light": "Fai spazio perché qualcosa arrivi.", "shadow": "Usi il mutismo come arma.", "question": "Quale silenzio è cura, e quale è punizione?", "message": "Tacere può essere la risposta più precisa."},
    {"id": "flame", "emoji": "🕯️", "it": "La Fiamma", "keys": "attenzione · spirito · veglia", "light": "Tieni una luce piccola, costante.", "shadow": "Ti consumi per illuminare tutti.", "question": "Cosa merita la tua attenzione stasera, e basta?", "message": "Una candela basta per una stanza. Non per la città."},
    {"id": "root", "emoji": "🪵", "it": "La Radice", "keys": "appartenenza · corpo · sotto", "light": "Sei tenuto. Non fluttui.", "shadow": "Restare inchiodato e chiamarlo lealtà.", "question": "Cosa ti tiene, quando tutto il resto si muove?", "message": "Senza radice ogni vento è un destino."},
    {"id": "wings", "emoji": "🪽", "it": "Le Ali", "keys": "slancio · visione · uscita", "light": "Prendi quota senza disprezzare il suolo.", "shadow": "Voli via al primo peso.", "question": "Da cosa hai bisogno di alzarti, non di scappare?", "message": "Le ali servono anche per atterrare."},
    {"id": "anchor", "emoji": "⚓", "it": "L'Ancora", "keys": "fermo · fede · porto", "light": "Scegli di restare.", "shadow": "Ti incateni e chiami stabilità.", "question": "Dove è giusto gettare l'ancora, e dove è paura?", "message": "Un'ancora si leva. Una catena no."},
    {"id": "companion", "emoji": "🤝", "it": "Il Compagno", "keys": "alleanza · fianco · noi", "light": "Non fai tutto da solo.", "shadow": "Ti appoggi per non stare in piedi.", "question": "Chi può stare al tuo fianco senza salvarti?", "message": "Compagnia è due schiene, non una stampella."},
    {"id": "solitary", "emoji": "🐺", "it": "Il Solitario", "keys": "autonomia · distanza · intero", "light": "Ti bastano le tue ossa.", "shadow": "Rifiuti il branco per orgoglio ferito.", "question": "Quale solitudine ti nutre, e quale ti indurisce?", "message": "Essere intero non è essere inaccessibile."},
    {"id": "messenger", "emoji": "🕊️", "it": "Il Messaggero", "keys": "notizia · ponte · consegna", "light": "Porti una parola al posto giusto.", "shadow": "Parli per tutti tranne che per te.", "question": "Quale messaggio è tuo, e quale stai solo recapitandolo?", "message": "Consegna e poi torna a casa."},
    {"id": "keeper", "emoji": "📦", "it": "Il Custode", "keys": "memoria · oggetto · sacro", "light": "Tieni ciò che non deve perdersi.", "shadow": "Accumuli per paura del vuoto.", "question": "Cosa vale la pena custodire, e cosa puoi restituire?", "message": "Custodire è un servizio, non un possessivo."},
    {"id": "rebel", "emoji": "⚡", "it": "Il Ribelle", "keys": "rottura · no · vita nuova", "light": "Rifiuti ciò che ti rimpicciolisce.", "shadow": "Dici no a tutto per sentirti libero.", "question": "Contro cosa ti stai ribellando, di preciso?", "message": "La ribellione vera costruisce dopo aver detto no."},
    {"id": "artist", "emoji": "🎨", "it": "L'Artista", "keys": "forma · gioco · verità visibile", "light": "Dai corpo a ciò che senti.", "shadow": "Estetica al posto della vita.", "question": "Cosa vuoi fare esistere, anche brutto e vero?", "message": "Creare è un modo di restare onesti."},
    {"id": "scholar", "emoji": "📚", "it": "Lo Studioso", "keys": "comprendere · mappa · lente", "light": "Vuoi capire prima di giudicare.", "shadow": "Studi per non vivere.", "question": "Cosa sai già abbastanza per agire?", "message": "C'è un punto in cui il libro si chiude e si esce."},
    {"id": "pilgrim", "emoji": "🥾", "it": "Il Pellegrino", "keys": "senso · strada · voto", "light": "Cammini verso qualcosa che ti eccede.", "shadow": "Rendi sacro ogni disagio.", "question": "Qual è il tuo voto, in una frase?", "message": "Il pellegrinaggio è direzione, non martirio."},
    {"id": "knot", "emoji": "🪢", "it": "Il Nodo", "keys": "intreccio · blocco · pazienza", "light": "Vedi dove i fili si sono stretti.", "shadow": "Tiri e stringi di più.", "question": "Quale nodo va slacciato, non tagliato?", "message": "I nodi si aprono con le dita, non con i denti."},
    {"id": "dawn", "emoji": "🌅", "it": "L'Alba", "keys": "inizio · chiarezza · fresco", "light": "Un ciclo nuovo, anche piccolo.", "shadow": "Ricominci per non finire mai.", "question": "Cosa inizia davvero stamattina, non solo 'da lunedì'?", "message": "L'alba non chiede un piano quinquennale."},
    {"id": "night", "emoji": "🌌", "it": "La Notte", "keys": "riposo · inconscio · limite", "light": "Smetti. Il giorno è finito.", "shadow": "Temi il buio e tieni tutte le luci accese.", "question": "Cosa puoi consegnare alla notte, senza risolverlo?", "message": "Dormire è un atto di fiducia."},
    {"id": "home", "emoji": "🏠", "it": "La Casa", "keys": "riparo · appartenenza · dentro", "light": "C'è un dentro in cui puoi posarti.", "shadow": "Chiudi fuori anche ciò che ti salverebbe.", "question": "Dove ti senti di casa, e dove fai solo finta?", "message": "Casa è un clima, non solo un indirizzo."},
)

# ---------------------------------------------------------------------------
# Animali — 72
# ---------------------------------------------------------------------------

ANIMALS: tuple[dict[str, str], ...] = (
    {"id": "wolf", "emoji": "🐺", "it": "Lupo", "keys": "istinto · branco · indipendenza", "message": "Il branco non annulla l'istinto. Lo affina.", "question": "Dove hai bisogno di fidarti maggiormente del tuo istinto?"},
    {"id": "fox", "emoji": "🦊", "it": "Volpe", "keys": "astuzia · adattamento · soglia", "message": "Non tutto si affronta di fronte. Alcune porte si girano.", "question": "Dove ti serve più strategia e meno ostinazione?"},
    {"id": "owl", "emoji": "🦉", "it": "Gufo", "keys": "visione notturna · silenzio · sapere", "message": "Vedi meglio quando gli altri dormono.", "question": "Quale verità si mostra solo al buio?"},
    {"id": "eagle", "emoji": "🦅", "it": "Aquila", "keys": "sguardo · quota · precisione", "message": "Dall'alto il sentiero è evidente. Poi si scende.", "question": "Cosa cambierebbe se guardassi da più in alto?"},
    {"id": "bear", "emoji": "🐻", "it": "Orso", "keys": "forza · letargo · tutela", "message": "A volte la forza è ritirarsi e nutrirsi.", "question": "Di quale riposo il tuo corpo sta facendo richiesta?"},
    {"id": "deer", "emoji": "🦌", "it": "Cervo", "keys": "sensibilità · eleganza · allerta", "message": "Sentire tutto non è debolezza. È un radar.", "question": "Cosa ti ha fatto tendere le orecchie, stamattina?"},
    {"id": "snake", "emoji": "🐍", "it": "Serpente", "keys": "muta · guarigione · pericolo", "message": "Lascia la pelle vecchia. Fa male e poi respira.", "question": "Quale pelle non ti sta più?"},
    {"id": "horse", "emoji": "🐴", "it": "Cavallo", "keys": "slancio · libertà · alleanza", "message": "La spinta c'è. Serve una direzione, non un freno eterno.", "question": "Dove stai tenendo le redini troppo strette?"},
    {"id": "cat", "emoji": "🐈", "it": "Gatto", "keys": "autonomia · piacere · confine", "message": "Avvicinati quando vuoi. Allontanati senza colpa.", "question": "Quale confine piccolo ti renderebbe più morbido?"},
    {"id": "dog", "emoji": "🐕", "it": "Cane", "keys": "lealtà · presenza · casa", "message": "Restare è un atto. Non una debolezza.", "question": "A chi — o a cosa — sei fedele, davvero?"},
    {"id": "raven", "emoji": "🐦‍⬛", "it": "Corvo", "keys": "presagio · intelligenza · soglia", "message": "Porta notizie scomode. Ascoltalo comunque.", "question": "Quale messaggio stai scacciando perché è nero?"},
    {"id": "swan", "emoji": "🦢", "it": "Cigno", "keys": "grazia · fedeltà · profondità", "message": "Sotto la superficie le zampe lavorano. Va bene così.", "question": "Cosa mostri di elegante, e cosa stai faticando in silenzio?"},
    {"id": "butterfly", "emoji": "🦋", "it": "Farfalla", "keys": "metamorfosi · leggerezza · breve", "message": "La bellezza qui è un passaggio, non una posa.", "question": "Quale stanza della crisalide stai vivendo adesso?"},
    {"id": "bee", "emoji": "🐝", "it": "Ape", "keys": "lavoro · dolce · comunità", "message": "Il miele arriva da mille voli, non da un gesto eroico.", "question": "Quale lavoro minuto sta già facendo il tuo alveare?"},
    {"id": "spider", "emoji": "🕷️", "it": "Ragno", "keys": "trama · pazienza · centro", "message": "Tessi e aspetti. Non insegui la mosca per tutta la stanza.", "question": "Quale rete stai costruendo, e per chi?"},
    {"id": "whale", "emoji": "🐋", "it": "Balena", "keys": "profondità · canto · memoria", "message": "C'è un oceano sotto le tue giornate. Scendi ogni tanto.", "question": "Quale emozione grande stai tenendo in apnea?"},
    {"id": "dolphin", "emoji": "🐬", "it": "Delfino", "keys": "gioco · intelletto · respiro", "message": "Si può essere intelligenti e ancora giocare.", "question": "Dove hai reso tutto troppo serio?"},
    {"id": "turtle", "emoji": "🐢", "it": "Tartaruga", "keys": "tempo · casa · protezione", "message": "Porti la casa con te. Non è un difetto.", "question": "Cosa puoi fare più lento senza perdere la strada?"},
    {"id": "lion", "emoji": "🦁", "it": "Leone", "keys": "cuore · territorio · voce", "message": "Ruggire serve. Anche riposare al sole.", "question": "Quale territorio è tuo, e quale stai solo occupando?"},
    {"id": "tiger", "emoji": "🐅", "it": "Tigre", "keys": "potenza · solitudine · precisione", "message": "Un balzo, non cento passettini nervosi.", "question": "Dove stai disperdendo una forza che andrebbe raccolta?"},
    {"id": "elephant", "emoji": "🐘", "it": "Elefante", "keys": "memoria · peso · famiglia", "message": "Non dimentichi. Usa la memoria per camminare, non per inchiodarti.", "question": "Quale ricordo sta guidando una scelta di oggi?"},
    {"id": "rabbit", "emoji": "🐇", "it": "Coniglio", "keys": "allerta · fertilità · fuga", "message": "Senti il pericolo prima. Poi scegli se correre.", "question": "Da cosa stai scappando che forse si può guardare?"},
    {"id": "hawk", "emoji": "🦅", "it": "Falco", "keys": "focus · preda · istante", "message": "Una cosa alla volta, vista bene.", "question": "Qual è la tua preda di questa settimana — in una parola?"},
    {"id": "dove", "emoji": "🕊️", "it": "Colomba", "keys": "pace · messaggio · ritorno", "message": "Porta tregua, non resa.", "question": "Dove puoi deporre le armi senza perdere dignità?"},
    {"id": "bat", "emoji": "🦇", "it": "Pipistrello", "keys": "eco · inversione · soglia", "message": "Vedi con altro senso. Il buio è un ambiente, non un errore.", "question": "Quale segnale stai sentendo di striscio, non di vista?"},
    {"id": "frog", "emoji": "🐸", "it": "Rana", "keys": "salto · acqua · voce", "message": "Di palude in palude, ma avanti.", "question": "Quale salto piccolo è disponibile oggi?"},
    {"id": "salmon", "emoji": "🐟", "it": "Salmone", "keys": "ritorno · fatica · origine", "message": "Risali il fiume perché qualcosa ti chiama a casa.", "question": "Verso quale origine stai nuotando, anche stanco?"},
    {"id": "owl2", "emoji": "🦉", "it": "Barbagianni", "keys": "ascolto · campo · apparizione", "message": "Arrivi silenzioso e cambi l'aria.", "question": "Cosa puoi fare senza annunciarlo?"},
    {"id": "stag", "emoji": "🦌", "it": "Cervo nobile", "keys": "orgoglio · ciclo · corona", "message": "I palchi cadono e ricrescono. Anche la tua corona.", "question": "Quale orgoglio puoi lasciare per questa stagione?"},
    {"id": "boar", "emoji": "🐗", "it": "Cinghiale", "keys": "carica · terra · determinazione", "message": "Vai dritto. Poi alza la testa.", "question": "Dove stai cinghialando senza vedere il bosco?"},
    {"id": "otter", "emoji": "🦦", "it": "Lontra", "keys": "gioco · acqua · destrezza", "message": "La vita non è solo attraversamento: è anche scivolare.", "question": "Quando hai giocato l'ultima volta, sul serio?"},
    {"id": "seal", "emoji": "🦭", "it": "Foca", "keys": "soglia · sogno · pelle", "message": "Tra terra e mare c'è la tua zona.", "question": "Quale mondo stai tradendo per stare sempre nell'altro?"},
    {"id": "owl3", "emoji": "🦉", "it": "Allocco", "keys": "domanda · umiltà · notte", "message": "Chiedere non è ignoranza. È apertura.", "question": "Quale domanda non hai fatto per paura di sembrare sciocco?"},
    {"id": "crow", "emoji": "🐦‍⬛", "it": "Cornacchia", "keys": "comunitario · furbo · città", "message": "Sopravvivi con intelligenza, non con posa selvaggia.", "question": "Quale risorsa stai ignorando perché 'non è poetica'?"},
    {"id": "peacock", "emoji": "🦚", "it": "Pavone", "keys": "mostrarsi · orgoglio · bellezza", "message": "Apri la ruota se è vero. Non se è una richiesta di applauso.", "question": "Dove hai paura di essere visto?"},
    {"id": "phoenix", "emoji": "🔥", "it": "Fenice", "keys": "rinascita · cenere · ciclo", "message": "Prima la cenere. Poi il volo. Non invertire.", "question": "Cosa sta bruciando, e cosa stai già ricostruendo?"},
    {"id": "dragon", "emoji": "🐉", "it": "Drago", "keys": "potere · tesoro · soglia", "message": "Il tesoro è custodito. Chiediti da chi.", "question": "Quale potere tuo stai parcheggiando fuori dalla vita?"},
    {"id": "unicorn", "emoji": "🦄", "it": "Unicorno", "keys": "raro · integro · visione", "message": "Non tutto ciò che è raro deve essere spiegato.", "question": "Quale parte integra non vuoi vendere?"},
    {"id": "owl_snow", "emoji": "🦉", "it": "Gufo delle nevi", "keys": "pazienza · bianco · attesa", "message": "Nel bianco si vede chi si muove.", "question": "Cosa diventa visibile se aspetti ancora un poco?"},
    {"id": "lynx", "emoji": "🐱", "it": "Lince", "keys": "segreto · vista · bosco", "message": "Vedi ciò che gli altri non nominano.", "question": "Quale dettaglio hai notato e stai fingendo di no?"},
    {"id": "panther", "emoji": "🐆", "it": "Pantera", "keys": "ombra · eleganza · potenza", "message": "Non devi ruggire per essere pericolosa/o. Devi essere intera/o.", "question": "Dove stai smorzando la tua presenza?"},
    {"id": "goat", "emoji": "🐐", "it": "Capra", "keys": "salita · ostinazione · equilibrio", "message": "La parete è verticale. I tuoi zoccoli no.", "question": "Quale salita stai evitando perché sembra ridicola?"},
    {"id": "ram", "emoji": "🐏", "it": "Montone", "keys": "testa · inizio · urto", "message": "A volte si parte con la testa. Poi si impara a usare anche il resto.", "question": "Dove stai sbattendo invece di girare?"},
    {"id": "bull", "emoji": "🐂", "it": "Toro", "keys": "materia · possesso · terra", "message": "Ciò che è tuo va tenuto. Ciò che non è tuo va rilasciato.", "question": "A cosa sei attaccato oltre il bisogno?"},
    {"id": "cow", "emoji": "🐄", "it": "Vacca", "keys": "nutrire · abbondanza · calma", "message": "Dare latte non è perdersi. È un mestiere.", "question": "Chi stai nutrendo, e chi nutre te?"},
    {"id": "pig", "emoji": "🐖", "it": "Maiale", "keys": "piacere · terra · intelligenza", "message": "Il fango non è vergogna. È materia.", "question": "Quale piacere semplice ti stai negando per morale?"},
    {"id": "sheep", "emoji": "🐑", "it": "Pecora", "keys": "gregge · morbidezza · seguito", "message": "Seguire non è sempre slealtà verso te. A volte è riposo.", "question": "Stai seguendo per convinzione o per paura di restare solo?"},
    {"id": "rooster", "emoji": "🐓", "it": "Gallo", "keys": "annuncio · territorio · alba", "message": "Canta quando è ora. Non tutta la notte.", "question": "Cosa è tempo di annunciare?"},
    {"id": "hen", "emoji": "🐔", "it": "Gallina", "keys": "cura · uovo · cortile", "message": "Tieni al caldo ciò che deve nascere.", "question": "Quale uovo stai covando senza dirtelo?"},
    {"id": "duck", "emoji": "🦆", "it": "Anatra", "keys": "superficie · famiglia · transito", "message": "Sembra calma. Sotto paga.", "question": "Cosa stai facendo sembrare facile?"},
    {"id": "goose", "emoji": "🪿", "it": "Oca", "keys": "migrazione · allarme · fedeltà", "message": "Parti con i tuoi. Grida se serve.", "question": "Con chi stai migrando, questa stagione?"},
    {"id": "crane", "emoji": "🦩", "it": "Gru", "keys": "longevità · danza · attesa", "message": "Stai su una gamba. È equilibrio, non povertà.", "question": "Quale attesa sta diventando danza?"},
    {"id": "heron", "emoji": "🐦", "it": "Airone", "keys": "pazienza · pesca · solitudine", "message": "Fermo. Poi il colpo. Non prima.", "question": "Dove stai pescando con troppa fretta?"},
    {"id": "pelican", "emoji": "🐦", "it": "Pellicano", "keys": "offerta · riserva · volo", "message": "Porti nel sacco più di quanto mostri.", "question": "Cosa stai dando, e cosa stai tenendo per il volo?"},
    {"id": "owl_barn", "emoji": "🦉", "it": "Civetta", "keys": "veglia · sapere · casa", "message": "Vegli sulla tua casa interiore.", "question": "Cosa succede nella tua casa quando tutti dormono?"},
    {"id": "mouse", "emoji": "🐭", "it": "Topo", "keys": "dettaglio · sopravvivenza · soglia", "message": "Le cose piccole rosicchiano i palazzi.", "question": "Quale dettaglio stai sottovalutando?"},
    {"id": "rat", "emoji": "🐀", "it": "Ratto", "keys": "adattamento · scarto · intelligenza", "message": "Sopravvivi dove altri recitano.", "question": "Quale risorsa 'brutta' ti sta salvando?"},
    {"id": "squirrel", "emoji": "🐿️", "it": "Scoiattolo", "keys": "scorta · salto · futuro", "message": "Nascondi noci. Non nascondere la vita.", "question": "Cosa stai accumulando, e per quale inverno?"},
    {"id": "hedgehog", "emoji": "🦔", "it": "Riccio", "keys": "difesa · morbidezza · rotolo", "message": "Dentro sei morbido. I aculei sono un mestiere, non un carattere.", "question": "Con chi puoi srotolarti?"},
    {"id": "mole", "emoji": "🦫", "it": "Talpa", "keys": "sotto · lavoro cieco · terra", "message": "Si avanza anche senza vedere il cielo.", "question": "Quale lavoro invisibile stai facendo, e chi lo sa?"},
    {"id": "beaver", "emoji": "🦫", "it": "Castoro", "keys": "costruire · diga · casa", "message": "Costruisci un mondo in cui poter stare.", "question": "Quale diga ti protegge, e quale ti allaga il prato?"},
    {"id": "badger", "emoji": "🦡", "it": "Tasso", "keys": "tana · tenacia · confine", "message": "Non molli la tana. Va bene. Esci anche.", "question": "Per cosa vale la pena essere ostinato?"},
    {"id": "fox_arctic", "emoji": "🦊", "it": "Volpe artica", "keys": "invisibile · inverno · cambio", "message": "Cambi pelo. Non è ipocrisia: è clima.", "question": "Quale adattamento stai giudicando come tradimento?"},
    {"id": "polar", "emoji": "🐻‍❄️", "it": "Orso polare", "keys": "estremo · solitudine · caccia", "message": "Il ghiaccio richiede rispetto, non pose.", "question": "In quale ambiente estremo stai insistendo?"},
    {"id": "penguin", "emoji": "🐧", "it": "Pinguino", "keys": "insieme · goffo · mare", "message": "In terra sei comico. In acqua sei esatto.", "question": "Qual è il tuo elemento, e dove stai recitando goffamente?"},
    {"id": "koala", "emoji": "🐨", "it": "Koala", "keys": "pausa · attacco · eucalipto", "message": "A volte la saggezza è dormire su un albero.", "question": "Cosa stai facendo solo perché gli altri sono svegli?"},
    {"id": "kangaroo", "emoji": "🦘", "it": "Canguro", "keys": "salto · marsupio · avanti", "message": "Porti il piccolo con te. E salti lo stesso.", "question": "Cosa stai portando addosso mentre provi ad avanzare?"},
    {"id": "camel", "emoji": "🐪", "it": "Cammello", "keys": "riserva · deserto · traversata", "message": "Hai già l'acqua per un tratto. Non drammatizzare ogni sete.", "question": "Quale riserva stai sottovalutando?"},
    {"id": "llama", "emoji": "🦙", "it": "Lama", "keys": "carico · altitudine · carattere", "message": "Porti. Non sei obbligato a sorridere.", "question": "Quale carico non è tuo?"},
    {"id": "octopus", "emoji": "🐙", "it": "Polpo", "keys": "molte braccia · inchiostro · intelligenza", "message": "Puoi fare più cose. Non tutte nello stesso secondo.", "question": "Quale braccio puoi ritirare senza morire?"},
    {"id": "jellyfish", "emoji": "🪼", "it": "Medusa", "keys": " deriva · contatto · confine", "message": "Morbida e urticante. Entrambe vere.", "question": "Dove sei troppo permeabile, e dove troppo velenosa/o?"},
    {"id": "starfish", "emoji": "⭐", "it": "Stella marina", "keys": "rigenerare · cinque · riva", "message": "Perdi un braccio, ne fai un altro. Tempo, non magia.", "question": "Cosa può ricrescere, se le dai stagione?"},
)

# ---------------------------------------------------------------------------
# Simboli — 36
# ---------------------------------------------------------------------------

SYMBOLS: tuple[dict[str, str], ...] = (
    {"id": "key", "emoji": "🗝️", "it": "La Chiave", "keys": "accesso · soluzione", "symbolism": "Apre ciò che era chiuso. A volte la porta, a volte una stanza in te.", "question": "Cosa può essere aperto?"},
    {"id": "mirror", "emoji": "🪞", "it": "Lo Specchio", "keys": "verità · volto", "symbolism": "Restituisce senza commento. Il lavoro è tenere lo sguardo.", "question": "Cosa ti sta rimandando questa situazione?"},
    {"id": "door", "emoji": "🚪", "it": "La Porta", "keys": "soglia · scelta", "symbolism": "Dentro o fuori. Restare sulla porta è una terza vita, faticosa.", "question": "Quale porta è davanti a te, e da che parte stai?"},
    {"id": "bridge", "emoji": "🌉", "it": "Il Ponte", "keys": "passaggio · rischio", "symbolism": "Due rive, un attraversamento. Il vuoto sotto fa parte del ponte.", "question": "Quale riva hai paura di lasciare?"},
    {"id": "candle", "emoji": "🕯️", "it": "La Candela", "keys": "attenzione · veglia", "symbolism": "Una fiamma piccola vince una stanza. Non una città.", "question": "Cosa merita la tua attenzione stasera?"},
    {"id": "spiral", "emoji": "🌀", "it": "La Spirale", "keys": "ritorno · centro", "symbolism": "Torni sugli stessi temi, più in dentro. Non è un fallimento.", "question": "A quale tema stai tornando, e a che profondità?"},
    {"id": "butterfly", "emoji": "🦋", "it": "La Farfalla", "keys": "muta · leggerezza", "symbolism": "La forma nuova non ricorda la vecchia. E va bene.", "question": "Quale crisalide stai abitano adesso?"},
    {"id": "tree", "emoji": "🌳", "it": "L'Albero", "keys": "radici · tempo", "symbolism": "Cresce dove sta. Le stagioni passano sui rami, non sul tronco.", "question": "Cosa in te è tronco, e cosa è solo foglia?"},
    {"id": "eye", "emoji": "🧿", "it": "L'Occhio", "keys": "sguardo · protezione", "symbolism": "Vedere e essere visti. Un occhio può custodire o controllare.", "question": "Chi sta guardando, e con quale intenzione?"},
    {"id": "ocean", "emoji": "🌊", "it": "L'Oceano", "keys": "emozione · vastità", "symbolism": "Non si possiede. Si naviga, o si sta sulla riva.", "question": "Quale emozione è più grande della tua barca, oggi?"},
    {"id": "star", "emoji": "⭐", "it": "La Stella", "keys": "orientamento · desiderio", "symbolism": "Non si raggiunge: si usa per non perdere il nord.", "question": "Quale stella stai usando come nord?"},
    {"id": "moon_s", "emoji": "🌙", "it": "La Luna", "keys": "ciclo · inconscio", "symbolism": "Cambia faccia e resta lo stesso corpo.", "question": "In quale fase sei, metaforicamente?"},
    {"id": "sun_s", "emoji": "☀️", "it": "Il Sole", "keys": "chiarezza · vita", "symbolism": "Rende visibile. Non negozia il giorno.", "question": "Cosa va portato alla luce, senza teatro?"},
    {"id": "cup", "emoji": "🏆", "it": "La Coppa", "keys": "cuore · offerta", "symbolism": "Si riempie e si versa. Una coppa chiusa non è un tesoro.", "question": "Cosa sei disposto a versare?"},
    {"id": "sword", "emoji": "⚔️", "it": "La Spada", "keys": "taglio · parola", "symbolism": "Separa il vero dal comodo. Taglia anche le mani se usata male.", "question": "Cosa va distinto, non fuso?"},
    {"id": "ring", "emoji": "💍", "it": "L'Anello", "keys": "patto · ciclo", "symbolism": "Unisce e può stringere. Il cerchio non ha uscita laterale.", "question": "A quale patto stai dicendo sì, ancora?"},
    {"id": "ladder", "emoji": "🪜", "it": "La Scala", "keys": "ascesa · tappa", "symbolism": "Un piolo alla volta. Saltare è cadere con stile.", "question": "Qual è il prossimo piolo, non la terrazza?"},
    {"id": "well", "emoji": "🪣", "it": "Il Pozzo", "keys": "profondità · sete", "symbolism": "L'acqua è sotto. Bisogna calare il secchio.", "question": "Cosa c'è in fondo, se hai il coraggio di calare?"},
    {"id": "seed_s", "emoji": "🌱", "it": "Il Seme", "keys": "inizio · buio", "symbolism": "Sembra niente. È già tutto, in miniatura.", "question": "Cosa hai piantato senza dirtelo?"},
    {"id": "crown", "emoji": "👑", "it": "La Corona", "keys": "ruolo · peso", "symbolism": "Si porta in testa. Pesa. Qualcuno la vuole, qualcuno la subisce.", "question": "Quale responsabilità è tua, e quale è teatro?"},
    {"id": "mask_s", "emoji": "🎭", "it": "La Maschera", "keys": "ruolo · nascondiglio", "symbolism": "Protegge e allontana. Utile in scena, pericolosa a colazione.", "question": "Quale maschera puoi togliere per un'ora?"},
    {"id": "thread", "emoji": "🧵", "it": "Il Filo", "keys": "legame · traccia", "symbolism": "Sottile e decisivo. Si perde, si riannoda, si taglia.", "question": "Quale filo non vuoi perdere?"},
    {"id": "knot_s", "emoji": "🪢", "it": "Il Nodo", "keys": "blocco · intreccio", "symbolism": "Si apre con le dita. I denti lo stringono.", "question": "Quale nodo va slacciato, non spezzato?"},
    {"id": "rose", "emoji": "🌹", "it": "La Rosa", "keys": "bellezza · spine", "symbolism": "Il profumo e il prezzo stanno sullo stesso stelo.", "question": "Stai cogliendo solo il fiore, o riconosci anche la spina?"},
    {"id": "stone", "emoji": "🪨", "it": "La Pietra", "keys": "peso · durata", "symbolism": "Non si discute. Si sposta, o si usa come fondamento.", "question": "Quale peso è fondamento, e quale è solo fatica?"},
    {"id": "fire_s", "emoji": "🔥", "it": "Il Fuoco", "keys": "passione · pericolo", "symbolism": "Scalda e brucia. La differenza è la misura.", "question": "Cosa stai alimentando, e con quanta legna?"},
    {"id": "feather", "emoji": "🪶", "it": "La Piuma", "keys": "messaggio · leggerezza", "symbolism": "Un segno piccolo. Se lo pretendi enorme, lo perdi.", "question": "Quale segnale lieve stai ignorando?"},
    {"id": "hourglass", "emoji": "⌛", "it": "La Clessidra", "keys": "tempo · fine", "symbolism": "La sabbia scende. Girarla è un altro ciclo, non l'eternità.", "question": "Di che tempo sei, in questa clessidra?"},
    {"id": "compass", "emoji": "🧭", "it": "La Bussola", "keys": "orientamento · scelta", "symbolism": "Non cammina al posto tuo. Dice il nord.", "question": "Qual è il tuo nord, questa settimana?"},
    {"id": "nest", "emoji": "🪺", "it": "Il Nido", "keys": "cura · fragile", "symbolism": "Si costruisce rametto per rametto. Si abbandona quando i piccoli volano.", "question": "Cosa stai covando, e quando è tempo di volo?"},
    {"id": "path", "emoji": "🛤️", "it": "Il Cammino", "keys": "direzione · passo", "symbolism": "Esiste perché qualcuno lo percorre. Non è un'autostrada.", "question": "Quale passo è il cammino, oggi?"},
    {"id": "mountain", "emoji": "⛰️", "it": "La Montagna", "keys": "prova · altezza", "symbolism": "Si sale. Si scende. Restare in vetta è un'altra storia.", "question": "Sei in salita, in cima, o già al ritorno?"},
    {"id": "valley", "emoji": "🏞️", "it": "La Valle", "keys": "riposo · mezzo", "symbolism": "Tra due monti c'è un luogo in cui si vive, non solo si transita.", "question": "Quale valle stai usando solo come corridoio?"},
    {"id": "fountain", "emoji": "⛲", "it": "La Fonte", "keys": "origine · sete", "symbolism": "L'acqua torna. Tu torna anche tu.", "question": "Di cosa hai sete, di preciso?"},
    {"id": "labyrinth_s", "emoji": "🌀", "it": "Il Labirinto", "keys": "perdita · centro", "symbolism": "Il centro non è l'uscita. A volte è il punto.", "question": "Stai cercando il centro o solo un'uscita?"},
    {"id": "lantern", "emoji": "🏮", "it": "La Lanterna", "keys": "guida · passo", "symbolism": "Illumina i piedi, non il paese.", "question": "Quale prossimo metro è abbastanza, stasera?"},
)

ELEMENTS: tuple[dict[str, str], ...] = (
    {"id": "fire", "emoji": "🔥", "it": "Fuoco", "keys": "azione · passione · chiarezza", "meaning": "Muove, illumina, consuma. Chiede un atto, non un piano eterno.", "question": "Cosa va acceso — o spento — oggi?"},
    {"id": "water", "emoji": "💧", "it": "Acqua", "keys": "emozione · adattamento · intuizione", "meaning": "Prende la forma del vaso. Sente prima di nominare. Può inondare.", "question": "Quale emozione sta chiedendo un alveo, non una diga?"},
    {"id": "air", "emoji": "🌬️", "it": "Aria", "keys": "pensiero · parola · distanza", "meaning": "Collega e disperde. Una buona idea ha bisogno di un corpo, dopo.", "question": "Cosa va detto, e cosa è solo vento mentale?"},
    {"id": "earth", "emoji": "🌍", "it": "Terra", "keys": "corpo · limite · costruzione", "meaning": "Ciò che sta. Cibo, casa, tempo, ossa. Non si discute: si abita.", "question": "Cosa di concreto puoi fare nelle prossime tre ore?"},
    {"id": "aether", "emoji": "✨", "it": "Etere", "keys": "senso · vuoto · legame", "meaning": "Lo spazio tra le cose. Significato, spirito, il 'perché' che non si tocca.", "question": "A cosa stai dando senso, e cosa è rimasto vuoto?"},
)

PLANET_ORACLE: tuple[dict[str, str], ...] = (
    {"id": "sun", "emoji": "☀️", "it": "Sole", "keys": "identità · vitalità · centro", "message": "Mostrati. Non tutta la vita è un retrobottega.", "question": "Dove puoi stare al centro senza scusarti?"},
    {"id": "moon", "emoji": "🌙", "it": "Luna", "keys": "umore · bisogno · memoria", "message": "Il sentire cambia faccia. Non è instabilità: è marea.", "question": "Di cosa hai bisogno, stasera, che non sia una prestazione?"},
    {"id": "mercury", "emoji": "☿️", "it": "Mercurio", "keys": "parola · scambio · mente", "message": "Nomina. Una frase chiara vale più di dieci pensieri.", "question": "Quale conversazione stai rimandando?"},
    {"id": "venus", "emoji": "♀️", "it": "Venere", "keys": "legame · piacere · valore", "message": "Cosa ami, e come lo tratti, parla di te più di ogni piano.", "question": "Dove stai togliendo bellezza per senso del dovere?"},
    {"id": "mars", "emoji": "♂️", "it": "Marte", "keys": "desiderio · conflitto · coraggio", "message": "Agisci o nomena la rabbia. Non farla diventare clima.", "question": "Cosa vuoi, in una frase, senza educarla?"},
    {"id": "jupiter", "emoji": "♃", "it": "Giove", "keys": "senso · espansione · fede", "message": "Allarga. Non per fuga: per aria.", "question": "Dove stai vivendo più piccolo del vero?"},
    {"id": "saturn", "emoji": "♄", "it": "Saturno", "keys": "struttura · limite · responsabilità", "message": "Il limite non è un insulto. È la forma che tiene.", "question": "Quale struttura ti sta chiedendo di diventare adulto, qui?"},
)

LUNAR_ORACLE: dict[str, dict[str, str]] = {
    "new": {
        "title": "🌑 NUOVA LUNA",
        "verb": "intenzione",
        "message": "Il cielo è scuro abbastanza da far posto a una riga tua. Non un voto solenne: un seme. Scrivilo. Non diluirlo.",
        "question": "Cosa vuoi che abbia spazio, in questo ciclo, anche se ancora non si vede?",
    },
    "waxing": {
        "title": "🌒 LUNA CRESCENTE",
        "verb": "costruzione",
        "message": "Si aggiunge, non si inaugura di nuovo. Un gesto ripetuto vale più di un piano. Costruisci il già scelto.",
        "question": "Quale mattone piccolo puoi posare oggi, senza aspettare l'ispirazione?",
    },
    "full": {
        "title": "🌕 LUNA PIENA",
        "verb": "consapevolezza",
        "message": "Si vede. Anche ciò che preferivi in penombra. Non è un verdetto: è un specchio alto. Nomina. Poi decide se tenere o lasciare.",
        "question": "Cosa è diventato evidente, e non vuoi ancora chiamare per nome?",
    },
    "waning": {
        "title": "🌘 LUNA CALANTE",
        "verb": "rilascio",
        "message": "Si toglie. Una chat, una scusa, un oggetto, una frase che non ti appartiene più. La chiusura è un mestiere, non un fallimento.",
        "question": "Cosa puoi lasciare in questo quarto, anche solo a voce?",
    },
}

ORACLE_QUESTIONS: tuple[str, ...] = (
    "Cosa stai continuando a fare soltanto perché hai paura di cambiare?",
    "Quale verità piccola stai già sapendo, ma non hai detto ad alta voce?",
    "Se potessi nominare la tua paura principale, come la chiameresti?",
    "Dove stai usando la forza, e dove basterebbe l'attenzione?",
    "Che cosa, se lo lasciassi andare, ti renderebbe più leggero?",
    "Quale parte di te chiede più spazio, in questo periodo?",
    "Cosa stai evitando di vedere chiaramente?",
    "A chi stai mentendo per prima: a te o all'altro?",
    "Quale bisogno semplice non hai chiesto?",
    "Se questa settimana fosse una stanza, dove sta la finestra?",
    "Cosa torneresti a curare, se avessi sette giorni più lenti?",
    "Quale 'devo' non è tuo?",
    "Dove ti stai facendo piccolo per stare in una relazione?",
    "Cosa accadrebbe se dicessi no tutto intero, una volta sola?",
    "Quale gioia stai rimandando come se fosse un lusso?",
    "Chi saresti senza questa scusa?",
    "Cosa ti sta chiedendo il corpo, che la testa non vuole sentire?",
    "Quale conversazione, se la facessi, ti restituirebbe aria?",
    "Dove stai aspettando un permesso che puoi darti tu?",
    "Se fossi già al sicuro, cosa proveresti adesso?",
)

DECKS: dict[str, tuple[dict[str, str], ...]] = {
    "arch": ARCHETYPES,
    "anim": ANIMALS,
    "symb": SYMBOLS,
    "elem": ELEMENTS,
    "plan": PLANET_ORACLE,
}

DECK_META = {
    "arch": ("🧿", "ORACOLO DEGLI ARCHETIPI", "Mazzo originale COSMOBOT. 48 figure."),
    "anim": ("🐺", "ORACOLO DEGLI ANIMALI", "Mazzo originale COSMOBOT. 72 animali."),
    "symb": ("🗝️", "ORACOLO DEI SIMBOLI", "Mazzo originale COSMOBOT. 36 segni."),
    "elem": ("🌿", "ORACOLO DEGLI ELEMENTI", "Fuoco, acqua, aria, terra, etere."),
    "plan": ("🪐", "ORACOLO PLANETARIO", "Sette pianeti classici, lettura simbolica. Non è un transito."),
}


def draw_deck(kind: str, count: int = 1) -> list[dict[str, str]]:
    pool = list(DECKS.get(kind) or ())
    if not pool:
        return []
    random.shuffle(pool)
    return [dict(card) for card in pool[: max(1, min(count, 3))]]


def lunar_key(phase: str) -> str:
    key = phase.lower()
    if "new" in key:
        return "new"
    if "full" in key:
        return "full"
    if "waning" in key or "last" in key or "third" in key:
        return "waning"
    if "waxing" in key or "first" in key:
        return "waxing"
    return "waxing"


def format_archetype(card: dict[str, str]) -> str:
    return (
        f"{card['emoji']} <b>{card['it'].upper()}</b>\n"
        f"<i>{card['keys']}</i>\n\n"
        f"✨ Luminoso: {card['light']}\n"
        f"🌑 Ombra: {card['shadow']}\n\n"
        f"💭 Domanda: {card['question']}\n\n"
        f"🔮 {card['message']}"
    )


def format_simple_card(card: dict[str, str], *, kind: str) -> str:
    if kind == "arch":
        return format_archetype(card)
    if kind == "symb":
        return (
            f"{card['emoji']} <b>{card['it'].upper()}</b>\n"
            f"<i>{card['keys']}</i>\n\n"
            f"🔮 Simbolismo\n{card['symbolism']}\n\n"
            f"💭 Domanda\n{card['question']}"
        )
    if kind == "elem":
        return (
            f"{card['emoji']} <b>{card['it'].upper()}</b>\n"
            f"<i>{card['keys']}</i>\n\n"
            f"{card['meaning']}\n\n"
            f"💭 {card['question']}"
        )
    return (
        f"{card['emoji']} <b>{card['it'].upper()}</b>\n"
        f"<i>{card['keys']}</i>\n\n"
        f"🔮 Messaggio\n{card['message']}\n\n"
        f"💭 Domanda\n{card['question']}"
    )


def format_lenormand_reading(
    drawn: list[dict[str, str]],
    positions: tuple[str, ...],
    question: str,
) -> str:
    lines = ["🌿 <b>LENORMAND</b>", "<i>Petit Lenormand · 36 carte</i>", ""]
    if question:
        lines.append(f"❓ <i>{question}</i>")
        lines.append("")
    for idx, card in enumerate(drawn):
        pos = positions[idx] if idx < len(positions) else f"Carta {idx + 1}"
        lines.append(
            f"{card['emoji']} <b>{card['it']}</b> · {pos}\n"
            f"<i>{card['keys']}</i>\n"
            f"{card['meaning']}"
        )
        lines.append("")
    if len(drawn) >= 2:
        lines.append("🔗 <b>Combinazioni</b>")
        lines.append(synthesize_lenormand(question, drawn))
        lines.append("")
    lines.append("<i>Nomi tradizionali. Testi del dataset COSMOBOT. Lettura simbolica, non previsione certa.</i>")
    return "\n".join(lines)


def yesno_from_rune() -> dict[str, str]:
    piece = draw_runes(1)[0]
    if piece["orientation"] == "reversed":
        lean, label = "no", "Inclinazione al NO"
    else:
        lean, label = "yes", "Inclinazione al SÌ"
    if piece["id"] in {"gebo", "isa"}:
        lean, label = "maybe", "Dipende / non ancora"
    return {
        "method": "🪶 Runa",
        "lean": lean,
        "label": label,
        "detail": f"{piece['glyph']} {piece['name']} · {piece['orientation']}\n{piece['meaning']}",
    }


def yesno_from_iching_lines(lines: list[int]) -> dict[str, str]:
    yang = sum(1 for value in lines if value in {7, 9})
    yin = 6 - yang
    changing = sum(1 for value in lines if value in {6, 9})
    if yang > yin:
        lean, label = "yes", "Inclinazione al SÌ"
    elif yin > yang:
        lean, label = "no", "Inclinazione al NO"
    else:
        lean, label = "maybe", "Equilibrio · non ancora"
    if changing >= 4:
        label += " (molte linee mutevoli: la situazione è in moto)"
    return {
        "method": "☯️ I Ching",
        "lean": lean,
        "label": label,
        "detail": f"{yang} linee yang, {yin} yin, {changing} mutevoli.",
    }


def yesno_from_tarot(reversed_card: bool, name: str) -> dict[str, str]:
    if reversed_card:
        lean, label = "no", "Inclinazione al NO"
    else:
        lean, label = "yes", "Inclinazione al SÌ"
    return {
        "method": "🃏 Tarocco",
        "lean": lean,
        "label": label,
        "detail": f"{name} · {'rovesciata' if reversed_card else 'diritta'}",
    }


def surprise_oracle() -> str:
    return random.choice(("tarot", "iching", "rune", "leno", "yes", "pietre"))


SKY_PLANET_FOLK: dict[str, str] = {
    "Mercury": "Mercurio in vista: la tradizione lo legge come messaggi e spostamenti.",
    "Venus": "Venere in vista: la tradizione la legge come gusto e legami.",
    "Mars": "Marte in vista: la tradizione lo legge come slancio e attrito.",
    "Jupiter": "Giove in vista: la tradizione lo legge come apertura e misura larga.",
    "Saturn": "Saturno in vista: la tradizione lo legge come limiti e tempo lungo.",
    "Uranus": "Urano in vista: la tradizione lo legge come scarto e novità.",
    "Neptune": "Nettuno in vista: la tradizione lo legge come nebbia e sogno.",
    "Pluto": "Plutone in vista: la tradizione lo legge come ciò che sta sotto e cambia.",
}


def sky_planet_folk(name_en: str) -> str:
    return SKY_PLANET_FOLK.get(name_en, "")


def interpret_asked_sky(
    *,
    place: str,
    phase_label: str,
    phase_message: str,
    visible: list[tuple[str, str]],
    night: bool,
    card_name: str = "",
) -> str:
    """Lettura simbolica del cielo reale. I pianeti visibili sono astronomia; il testo è folklore."""
    bits: list[str] = []
    if night:
        bits.append(f"Sopra {place} è notte: la tradizione legge il cielo come stanza aperta.")
    else:
        bits.append(f"Sopra {place} è giorno: la tradizione legge il cielo come lavoro alla luce.")
    if phase_label:
        bits.append(f"La Luna è {phase_label}. {phase_message}".strip())
    folk = [sky_planet_folk(key) for key, _label in visible if sky_planet_folk(key)]
    bits.extend(folk[:4])
    if not folk and visible:
        names = ", ".join(label for _key, label in visible[:4])
        bits.append(f"In vista: {names}. La tradizione li tiene come testimoni, non come ordini.")
    if not visible:
        bits.append("Nessun pianeta sopra l'orizzonte in questo istante: il cielo chiede attesa, non un verdetto.")
    if card_name:
        bits.append(f"Il segno pescato è {card_name}: un'immagine in più, non un destino.")
    bits.append("Il cielo misurato è astronomia. Questa lettura è uno specchio, non una previsione.")
    return " ".join(bit for bit in bits if bit)
