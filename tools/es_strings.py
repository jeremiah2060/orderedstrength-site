#!/usr/bin/env python3
"""The Spanish wording for this site. es-419, to match the app.

REGISTER. The app addresses the athlete as "tú" (its own catalog says "Tu RIR", "Tus datos"),
so the site does too. A Spanish page that says "usted" while the app it is selling says "tú"
is two products talking.

THE ONE RULE. Anything the app SAYS is not translated here. It is looked up in the app's own
catalog by `app-strings.py` and pasted in as APP, below. Translating those would make the
Spanish page claim the product says words it has never said, which is the failure browser
auto-translate produced and the reason this file exists.
"""

# ── What the APP says, taken from Localizable.xcstrings, never invented here ────────────
#
# 🔒 NOT IN USE YET, AND THE REASON IS THE SHOT GATE DOING ITS JOB. Every <code> run on this
# site is asserted against the PIXELS of a published screenshot. The Spanish captures are
# currently broken: `ColdStart_Session1_es419` and `ColdStart_Session100_es419` both photograph
# the DAY ZERO screen ("Aún sin sesiones", "Población", "Comienza Tu Primera Sesión"), because
# the fixture looks its six lifts up by ENGLISH name and the Spanish arm's session-count
# assertion was deliberately disabled. So the Spanish pages publish the ENGLISH photographs,
# and a caption quoting "Calibración (Construyendo)" over a picture that says
# "Calibration (Building)" would be a lie the gate would correctly refuse to ship.
#
# THEREFORE: quoted app strings stay ENGLISH on the Spanish pages, the prose around them is
# Spanish, and one line tells the reader the app itself runs in Spanish and these frames are
# the English build. The moment trustworthy es captures exist, the images and this map get
# swapped in the SAME commit, and shot-gate proves the pair.
APP_WHEN_ES_CAPTURES_EXIST = {
    'Barbell Back Squat':              'Sentadilla Trasera con Barra',
    'Building':                        'Construyendo',
    'Calibration (Building)':          'Calibración (Construyendo)',
    'Calibration (Your RIR)':          'Calibración (Tu RIR)',
    'Individual Recovery Fingerprint': 'Huella individual de recuperación',
    'Metabolic Phenotype':             'Fenotipo metabólico',
    'Pop. Est.':                       'Est. pobl.',
    'Your Data':                       'Tus datos',
    # Composed at runtime in the app, so no single catalog row exists. Rendered from the
    # Spanish captures once those are trustworthy; until then these are the app's own
    # published es wording for the same surfaces, transcribed rather than translated.
    'Session 100':                     'Sesión 100',
    'Session 1':                       'Sesión 1',
    '100 sessions logged':             '100 sesiones registradas',
    'Each one names the evidence I still need.':
        'Cada una nombra la evidencia que todavía necesito.',
    'open on evidence, not time':      'se abren con evidencia, no con el tiempo',
    'Your load and your recovery rate are both measured from you now':
        'Tu carga y tu tasa de recuperación ahora se miden a partir de ti',
}


# Until then, no <code> run is translated.
APP = {}

# ── Chrome shared by every page ─────────────────────────────────────────────────────────
CHROME = {
    'How it works': 'Cómo funciona',
    'Stronger': 'Más fuerte',
    'The record': 'El registro',
    'Verify': 'Verificar',
    'Join the test': 'Únete a la prueba',
    'The product': 'El producto',
    'Getting stronger': 'Ponerse más fuerte',
    'Published anchors': 'Anclas publicadas',
    'Verify a receipt': 'Verificar un comprobante',
    'The small print': 'La letra chica',
    'Privacy': 'Privacidad',
    'Support': 'Soporte',
    'iPhone &middot; in testing': 'iPhone &middot; en pruebas',
    'Your training is computed on your device':
        'Tu entrenamiento se calcula en tu dispositivo',
    'A strength coach for iPhone that writes each session down before you lift, then grades\n      itself on what it wrote.':
        'Un coach de fuerza para iPhone que anota cada sesión antes de que levantes, y después\n      se califica a sí mismo con lo que escribió.',
    # Scoped with its markup: bare 'Build' is a substring of 'Building'.
    '<span>Build ': '<span>Compilación ',
}

# ── /record/ ────────────────────────────────────────────────────────────────────────────
RECORD = {
    'The record · OrderedStrength': 'El registro · OrderedStrength',
    'The public accuracy record. What it will contain, what it proves, and an honest statement that it has not started yet.':
        'El registro público de precisión. Qué contendrá, qué prueba, y una declaración honesta de que todavía no empieza.',
    'Every call he makes, graded. Including the ones he got wrong.':
        'Cada decisión que toma, calificada. Incluidas las que erró.',
    'We have not found another app in this market that publishes how often it\n    was right. If one exists, tell us and we will link it. This page is where ours goes, and it\n    is published before we charge anyone.':
        'No hemos encontrado otra app en este mercado que publique con qué frecuencia acertó. Si\n    existe alguna, dínoslo y la enlazamos. Esta página es donde va el nuestro, y se publica antes\n    de cobrarle a nadie.',
    'Daily commitment anchors': 'Anclas diarias de compromiso',
    'checking': 'consultando',
    'Not started yet.': 'Todavía no empieza.',
    'Reading the public repository.': 'Leyendo el repositorio público.',
    'Two different claims': 'Dos afirmaciones distintas',
    'What a receipt proves, and what only the anchor can.':
        'Lo que prueba un comprobante, y lo que solo el ancla puede probar.',
    'Was it edited afterwards?': '¿Se editó después?',
    'ANSWERABLE TODAY': 'SE PUEDE RESPONDER HOY',
    'Was it really made beforehand?': '¿De verdad se hizo antes?',
    'NOT YET ANSWERABLE': 'TODAVÍA NO SE PUEDE RESPONDER',
    'verifier': 'verificador',
    'home page': 'página principal',
    'A receipt carries the prediction, a random nonce, and a fingerprint taken over both. Recompute it and you know whether a single character moved. You can do that right now on the ':
        'Un comprobante lleva la predicción, un nonce aleatorio y una huella tomada sobre ambos. Vuelve a calcularla y sabrás si se movió un solo carácter. Puedes hacerlo ahora mismo en el ',
    'That needs a timestamp we do not control. Publishing one root hash per day to a public repository gives it: the commit dates come from GitHub, not from us. Until the first anchor lands, we say so rather than implying a proof we do not have.':
        'Eso necesita una marca de tiempo que no controlamos. Publicar un hash raíz por día en un repositorio público la da: las fechas de los commits vienen de GitHub, no de nosotros. Hasta que aterrice la primera ancla, lo decimos en vez de insinuar una prueba que no tenemos.',
    'Why it starts empty': 'Por qué empieza vacío',
    'Backfilling would destroy the only thing this is for.':
        'Rellenarlo hacia atrás destruiría lo único para lo que sirve.',
    'We could generate anchors for every prediction already sealed on a phone and\n    publish them today. The page would look established. It would also be worthless, because a\n    record assembled after the results were known proves nothing about when anything was decided.':
        'Podríamos generar anclas para cada predicción ya sellada en un teléfono y publicarlas hoy.\n    La página se vería establecida. También sería inútil, porque un registro armado después de\n    conocer los resultados no prueba nada sobre cuándo se decidió cada cosa.',
    'So the record starts on the day it starts, and the gap before it is stated\n    rather than hidden. That is the whole product in one decision.':
        'Así que el registro empieza el día que empieza, y el vacío anterior se declara en vez de\n    esconderse. Ese es el producto entero en una sola decisión.',
    'Source:': 'Fuente:',
    'Read live from GitHub each time this page loads, so what you see here is what the repository\n      actually contains rather than a number we typed.':
        'Se lee en vivo desde GitHub cada vez que carga esta página, así que lo que ves aquí es lo\n      que el repositorio realmente contiene y no un número que escribimos nosotros.',
}

RECORD_SCRIPT = {
    "'none yet'": "'ninguna todavía'",
    "'<div class=\"empty\"><h3>No anchors published yet.</h3>'":
        "'<div class=\"empty\"><h3>Todavía no hay anclas publicadas.</h3>'",
    "'When the first one lands, this list fills with one line per day: the date, and the root '":
        "'Cuando aterrice la primera, esta lista se llena con una línea por día: la fecha y el hash '",
    "'hash covering every prediction sealed that day. Nothing else, forever.</p></div>'":
        "'raíz que cubre cada predicción sellada ese día. Nada más, para siempre.</p></div>'",
    "'The repository exists and the anchor folder has not been created yet, which is the honest state on '":
        "'El repositorio existe y la carpeta de anclas todavía no se ha creado, que es el estado honesto al '",
    "'The anchor folder exists but holds no published roots yet.'":
        "'La carpeta de anclas existe pero todavía no contiene raíces publicadas.'",
    "' published'": "' publicadas'",
    "'unreachable'": "'inalcanzable'",
    "'<div class=\"empty\"><h3>Could not read the repository.</h3>'":
        "'<div class=\"empty\"><h3>No se pudo leer el repositorio.</h3>'",
    "'<p>GitHub did not answer, so this page will not guess at a number. '":
        "'<p>GitHub no respondió, así que esta página no va a adivinar un número. '",
    "'Open the repository directly</a> and read it yourself.</p></div>'":
        "'Abre el repositorio directamente</a> y léelo tú mismo.</p></div>'",
}


# ── /404.html ───────────────────────────────────────────────────────────────────────────
NOTFOUND = {
    'Not found · OrderedStrength': 'No encontrado · OrderedStrength',
    'That page is not here. The pages that are: how it works, the record, the receipt verifier, and how to join the test.':
        'Esa página no está aquí. Las que sí están: cómo funciona, el registro, el verificador de comprobantes, y cómo unirte a la prueba.',
    'There is nothing at this address.': 'No hay nada en esta dirección.',
    'Rather than guess where you were going, here is everything there is.':
        'En vez de adivinar a dónde ibas, esto es todo lo que hay.',
    'Home': 'Inicio',
}

# ── /verify/ ────────────────────────────────────────────────────────────────────────────
VERIFY = {
    'Verify a receipt · OrderedStrength': 'Verificar un comprobante · OrderedStrength',
    'Paste a receipt copied from OrderedStrength and check whether the prediction inside it is byte for byte the one that was sealed before the set.':
        'Pega un comprobante copiado desde OrderedStrength y revisa si la predicción que lleva dentro es, byte por byte, la que se selló antes de la serie.',
    'Verifier': 'Verificador',
    'Check a receipt.': 'Revisa un comprobante.',
    'Paste a receipt copied from OrderedStrength. This checks whether the prediction inside it is byte for byte the one that was sealed before the set was performed. No account, no sign in, and nothing you paste is stored.':
        'Pega un comprobante copiado desde OrderedStrength. Esto revisa si la predicción que lleva dentro es, byte por byte, la que se selló antes de hacer la serie. Sin cuenta, sin iniciar sesión, y nada de lo que pegues se guarda.',
    'Receipt JSON': 'JSON del comprobante',
    'Check it': 'Revisarlo',
    'Use a sample receipt': 'Usar un comprobante de ejemplo',
    'the record': 'el registro',
}

VERIFY_SCRIPT = {
    # The verifier prints its recomputed fingerprint behind a one-word label built inside the
    # JS. It is not an app string, it is this page's own word, so it translates. Left English it
    # would be the single English word on an otherwise Spanish verdict card.
    '<code translate="no">computed \'+computed+\'</code>':
        '<code translate="no">calculada \'+computed+\'</code>',
    "'The fingerprint matches. This prediction is byte for byte the one that was sealed.'":
        "'La huella coincide. Esta predicción es, byte por byte, la que se selló.'",
    "'This receipt did not verify.'": "'Este comprobante no se verificó.'",
    "'Paste a receipt into the box above, or press the sample button.'":
        "'Pega un comprobante en el cuadro de arriba, o presiona el botón de ejemplo.'",
    "'Paste the receipt exactly as it was copied, including the outer brackets.'":
        "'Pega el comprobante exactamente como se copió, incluyendo las llaves exteriores.'",
    "'The verification service is not reachable at this address. This says nothing about your receipt.'":
        "'El servicio de verificación no está disponible en esta dirección. Esto no dice nada sobre tu comprobante.'",
    "'The request did not complete. This says nothing about your receipt.'":
        "'La solicitud no se completó. Esto no dice nada sobre tu comprobante.'",
}

# ── /join/ ──────────────────────────────────────────────────────────────────────────────
JOIN = {
    'Join the test · OrderedStrength': 'Únete a la prueba · OrderedStrength',
    'How to get into the OrderedStrength test on iPhone. No waiting list and no account system: you write to a person, and a person writes back.':
        'Cómo entrar a la prueba de OrderedStrength en iPhone. Sin lista de espera y sin sistema de cuentas: le escribes a una persona, y una persona te responde.',
    'There is no waiting list, because there is no list.':
        'No hay lista de espera, porque no hay lista.',
    'No account system exists yet, so there is nothing here that could hold your email address without us building the exact thing this product refuses to build. Write to a person instead. A person writes back.':
        'Todavía no existe un sistema de cuentas, así que aquí no hay nada que pueda guardar tu correo sin que construyamos exactamente lo que este producto se niega a construir. Mejor escríbele a una persona. Una persona te responde.',
    'Write to us': 'Escríbenos',
    'Read how it works first': 'Primero lee cómo funciona',
    'What happens next': 'Qué pasa después',
    'Four steps, and none of them are automated.': 'Cuatro pasos, y ninguno está automatizado.',
    'You write, with three answers': 'Escribes, con tres respuestas',
    'The button above opens a message with three questions already in it: how long you have trained, what you train on and how often, and what you use now. Answer them in one line each. That is the whole application.':
        'El botón de arriba abre un mensaje con tres preguntas ya escritas: cuánto tiempo llevas entrenando, en qué entrenas y con qué frecuencia, y qué usas ahora. Respóndelas en una línea cada una. Esa es toda la postulación.',
    'A person reads it': 'Una persona lo lee',
    'Not a form handler and not a queue. The test is small on purpose, because a coaching engine is only worth testing against people whose training we can actually follow.':
        'No es un formulario ni una fila. La prueba es pequeña a propósito, porque un motor de coaching solo vale la pena probarlo con gente cuyo entrenamiento podamos seguir de verdad.',
    'You get a TestFlight invitation, or an honest no':
        'Recibes una invitación de TestFlight, o un no honesto',
    'If the build is not right for how you train yet, we say that instead of adding you to a list and going quiet.':
        'Si la versión todavía no encaja con cómo entrenas, lo decimos en vez de meterte en una lista y quedarnos callados.',
    'You are asked for one thing': 'Se te pide una sola cosa',
    'Rate your effort honestly after each set. Round up to look strong and the coach learns a fake version of you, which helps nobody and costs you months of training.':
        'Califica tu esfuerzo con honestidad después de cada serie. Si lo inflas para verte fuerte, el coach aprende una versión falsa de ti, que no le sirve a nadie y te cuesta meses de entrenamiento.',
    'What you are agreeing to': 'A qué estás accediendo',
    'Nothing that needs a checkbox.': 'Nada que necesite una casilla.',
    'privacy policy': 'política de privacidad',
    'Your email address exists in one place, which is the message you sent, in an inbox. It is not in a mailing tool, it is not in a customer database, and it is not synced anywhere. If you would rather it were not there at all, say so in the message and it goes.':
        'Tu correo existe en un solo lugar, que es el mensaje que enviaste, en una bandeja de entrada. No está en una herramienta de envíos, no está en una base de datos de clientes, y no se sincroniza a ningún lado. Si prefieres que no esté ahí en absoluto, dilo en el mensaje y se va.',
    'The app is in testing on iPhone. It is not on the App Store yet. When it ships, the price is 199 US dollars per year with 14 days free, and the accuracy record is published before anyone is charged.':
        'La app está en pruebas en iPhone. Todavía no está en la App Store. Cuando salga, el precio es 199 dólares al año con 14 días gratis, y el registro de precisión se publica antes de cobrarle a nadie.',
}


# ── /stronger/ ──────────────────────────────────────────────────────────────────────────
STRONGER = {
    'Getting stronger · OrderedStrength': 'Ponerse más fuerte · OrderedStrength',
    'What actually happens to your body: inside one set, across one week, across months. And the results claim we will not make until we have earned it.':
        'Lo que de verdad le pasa a tu cuerpo: dentro de una serie, a lo largo de una semana, a lo largo de meses. Y la afirmación sobre resultados que no vamos a hacer hasta habérnosla ganado.',
    'What actually gets heavier': 'Qué se pone más pesado de verdad',
    'The weight on the bar is the only number that has to go up.':
        'El peso en la barra es el único número que tiene que subir.',
    'You did not come here to audit a coach. You came because you want to lift more than you lifted last month. Jerry works on three time scales to get you there: the set you are standing over, the week you are in, and the months you have been at it.':
        'No viniste aquí a auditar a un coach. Viniste porque quieres levantar más de lo que levantaste el mes pasado. Jerry trabaja en tres escalas de tiempo para llevarte ahí: la serie que tienes delante, la semana en la que estás, y los meses que llevas.',
    'Three time scales': 'Tres escalas de tiempo',
    'Strength is built across a set, a week and a run of months. He works all three.':
        'La fuerza se construye en una serie, en una semana y en una racha de meses. Él trabaja las tres.',
    'Inside one set': 'Dentro de una serie',
    'He watches the reps land, then writes the next one.':
        'Mira cómo caen las repeticiones, y después escribe la siguiente serie.',
    'You finish a set and tell him how many reps you had left. If you hit failure under the load he asked for, the next set comes down by five percent, or by one real plate step, whichever is further. That brake fires inside the session, not next week. Close to failure is what grows muscle. Getting strong is mostly load and clean reps, so he leaves reps in reserve on your heavy sets.':
        'Terminas una serie y le dices cuántas repeticiones te quedaban. Si llegas al fallo por debajo de la carga que te pidió, la siguiente serie baja un cinco por ciento, o un escalón real de disco, lo que sea más profundo. Ese freno se activa dentro de la sesión, no la semana que viene. Acercarse al fallo es lo que hace crecer el músculo. Ponerse fuerte es sobre todo carga y repeticiones limpias, así que te deja repeticiones en reserva en las series pesadas.',
    'Across one week': 'A lo largo de una semana',
    'Enough work to grow, and a stop before it becomes a hole.':
        'Trabajo suficiente para crecer, y un alto antes de que se vuelva un hoyo.',
    'Muscle comes from doing more than your body is used to and then recovering from it. The second half is the one people skip, so Jerry counts what each muscle has taken across the week and cuts the session when the arithmetic says you are borrowing from next week rather than earning this one. Some weeks he asks for less than you came in willing to give. He watches the floor as well as the ceiling: under a weekly minimum a muscle gets no growth signal at all, and he will tell you which one is under it.':
        'El músculo viene de hacer más de lo que tu cuerpo está acostumbrado y después recuperarte de eso. La segunda mitad es la que la gente se salta, así que Jerry cuenta lo que ha recibido cada músculo durante la semana y recorta la sesión cuando la cuenta dice que le estás pidiendo prestado a la semana que viene en vez de ganarte esta. Algunas semanas te pide menos de lo que venías dispuesto a dar. Vigila el piso igual que el techo: por debajo de un mínimo semanal un músculo no recibe ninguna señal de crecimiento, y él te dirá cuál está por debajo.',
    'Across the months': 'A lo largo de los meses',
    'The reps come first. Then the plate goes on.':
        'Primero llegan las repeticiones. Después entra el disco.',
    'While you are building, the weight moves on your reps and not on the week: hit the top of the rep range once at the effort he asked for and the plate goes on, after which the target drops to the middle and the climb starts again. That is double progression. In an overreach or a recovery week the plan sets the percentage instead, and he tells you which week you are in. What you watch climb is your estimated one rep max, and the word estimated is carrying real weight there. Nobody measured it under a bar. It is computed from the loads, the reps and the reserve you reported.':
        'Mientras construyes, el peso se mueve con tus repeticiones y no con la semana: llega una vez al tope del rango con el esfuerzo que te pidió y entra el disco, y después el objetivo baja a la mitad del rango y la subida vuelve a empezar. Eso es doble progresión. En una semana de sobrecarga o de recuperación es el plan el que fija el porcentaje, y él te dice en qué semana estás. Lo que ves subir es tu máximo de una repetición estimado, y la palabra estimado ahí pesa de verdad. Nadie lo midió bajo una barra. Se calcula a partir de las cargas, las repeticiones y la reserva que reportaste.',
    'The claim we will not make': 'La afirmación que no vamos a hacer',
    'There is no before and after photograph on this site.':
        'En este sitio no hay foto de antes y después.',
    'Results data': 'Datos de resultados',
    'none yet': 'todavía ninguno',
    'There is no results dataset. The test group has not trained long enough, so any number here about how much stronger anyone got would be invented.':
        'No hay un conjunto de datos de resultados. El grupo de prueba no lleva entrenando el tiempo suficiente, así que cualquier número aquí sobre cuánto más fuerte se puso alguien sería inventado.',
    'the record': 'el registro',
    'Where to start': 'Por dónde empezar',
    'Train for a few months and check his work.':
        'Entrena unos meses y revisa su trabajo.',
    'how it works': 'cómo funciona',
}

# ── /support/ ───────────────────────────────────────────────────────────────────────────
SUPPORT = {
    'Support · OrderedStrength': 'Soporte · OrderedStrength',
    'Contact and common questions for the OrderedStrength iPhone app.':
        'Contacto y preguntas frecuentes de la app OrderedStrength para iPhone.',
    'OrderedStrength Support': 'Soporte de OrderedStrength',
    'OrderedStrength is a strength-training app for iPhone. If something is wrong, or a number looks wrong, we want to hear about it.':
        'OrderedStrength es una app de entrenamiento de fuerza para iPhone. Si algo está mal, o un número se ve mal, queremos saberlo.',
    'Contact': 'Contacto',
    'Telling us your iPhone model, your iOS version, and what you were doing when it happened will usually get you an answer in one reply instead of three.':
        'Si nos dices tu modelo de iPhone, tu versión de iOS y qué estabas haciendo cuando pasó, normalmente te respondemos en un solo mensaje en vez de tres.',
    'Common questions': 'Preguntas frecuentes',
    'Where is my training stored, and what happens if I lose my phone?':
        '¿Dónde se guarda mi entrenamiento, y qué pasa si pierdo el teléfono?',
    'privacy policy': 'política de privacidad',
    'Why does the coach sometimes say it does not know yet?':
        '¿Por qué a veces el coach dice que todavía no sabe?',
    'Because it does not. The app starts from population research and tells you so, and it moves onto your own numbers as your logged sets accumulate. It is built to say what it is unsure of rather than sound confident and be wrong.':
        'Porque de verdad no sabe. La app parte de investigación poblacional y te lo dice, y se va moviendo hacia tus propios números conforme se acumulan las series que registras. Está hecha para decir de qué no está segura en vez de sonar segura y equivocarse.',
    'Why does the voice sound like the standard iPhone voice?':
        '¿Por qué la voz suena como la voz estándar del iPhone?',
    'The natural voice needs a network connection. When it cannot reach the service, the app falls back to the built-in system voice so the coaching never goes silent mid-set.':
        'La voz natural necesita conexión de red. Cuando no puede alcanzar el servicio, la app usa la voz del sistema para que el coaching nunca se quede mudo a mitad de una serie.',
    'How do I stop the app sharing anything at all?':
        '¿Cómo hago que la app no comparta absolutamente nada?',
    'How do I delete everything?': '¿Cómo borro todo?',
    'Important': 'Importante',
    'OrderedStrength is a training tool, not a medical service. Nothing in it is a diagnosis or a treatment plan. If something hurts, or you are managing an injury or a health condition, a qualified healthcare professional decides, not the app.':
        'OrderedStrength es una herramienta de entrenamiento, no un servicio médico. Nada en ella es un diagnóstico ni un plan de tratamiento. Si algo te duele, o estás manejando una lesión o una condición de salud, decide un profesional de la salud calificado, no la app.',
}


# ── / (home) ────────────────────────────────────────────────────────────────────────────
# The mockups on this page are LIVE HTML, not photographs, so the app words inside them are
# rendered in Spanish: a Spanish reader running the Spanish app would see Spanish there.
# Exercise names and "Población" come from the app's own catalog. "Within", "Outside",
# "logged" and "withdrawn" have no catalog row (they are composed or are this page's own
# labels), so they are translated here and marked as such.
HOME = {
    'Strength coaching for iPhone': 'Coaching de fuerza para iPhone',
    'He changes your workout in the middle of it.':
        'Te cambia el entrenamiento a la mitad.',
    'See him cut a set': 'Míralo recortar una serie',
    'Prediction accuracy': 'Precisión de la predicción',
    'Bulgarian Split Squat': 'Sentadilla Búlgara',
    'Romanian Deadlift': 'Peso Muerto Rumano',
    'Incline Barbell Press': 'Press Inclinado con Barra',
    'Within': 'Dentro',
    'Outside': 'Fuera',
    'Sealed before the set': 'Sellado antes de la serie',
    'The prediction is fingerprinted before your first rep. Change one character of it afterwards and the fingerprint stops matching.':
        'La predicción recibe su huella antes de tu primera repetición. Cambia un solo carácter después y la huella deja de coincidir.',
    'Graded where you can read it': 'Calificado donde puedes leerlo',
    'Hits and misses both. Nothing is deleted to make him look better.':
        'Los aciertos y los fallos. No se borra nada para que se vea mejor.',
    'The coaching runs on your phone': 'El coaching corre en tu teléfono',
    'Every decision is computed on your device. No account, no password, nothing to log into.':
        'Cada decisión se calcula en tu dispositivo. Sin cuenta, sin contraseña, sin nada donde iniciar sesión.',
    'What he actually does': 'Lo que realmente hace',
    'He decides, then he reacts.': 'Decide, y después reacciona.',
    'A logbook remembers. A plan hands you a program and stops listening. Jerry picks the lift, sets the load, and then changes the rest of the session the moment your reserve tells him the day is not going the way he thought.':
        'Una bitácora recuerda. Un plan te entrega un programa y deja de escuchar. Jerry elige el ejercicio, fija la carga, y después cambia el resto de la sesión en cuanto tu reserva le dice que el día no va como esperaba.',
    'He holds the load, asks for one more rep, and adds the plate once you have earned it.':
        'Mantiene la carga, te pide una repetición más, y agrega el disco una vez que te lo ganaste.',
    'Back Squat': 'Sentadilla trasera',
    'set 3 of 4': 'serie 3 de 4',
    'Set 1': 'Serie 1', 'Set 2': 'Serie 2', 'Set 3': 'Serie 3', 'Set 4': 'Serie 4',
    # 🔒 SCOPED, NOT BARE. These are mockup labels and each is also a common English word
    # inside sentences elsewhere on the page. Keyed with their markup so a substitution
    # cannot reach into prose: 'logged' bare rewrote "after one logged session".
    '>logged<': '>registrada<',
    '>withdrawn<': '>retirada<',
    'You are fading faster than I planned. I am cutting the last set. That protects tomorrow more than one more hard set helps today.':
        'Estás cayendo más rápido de lo que planeé. Voy a recortar la última serie. Eso protege el mañana más de lo que una serie dura más ayuda hoy.',
    'You add the plate the week you earn it':
        'Agregas el disco la semana en que te lo ganas',
    'Not the week a calendar says. The load moves when you finish the top of the rep range at the effort he asked for, and it holds when you do not.':
        'No la semana que diga un calendario. La carga se mueve cuando terminas el tope del rango de repeticiones con el esfuerzo que te pidió, y se queda igual cuando no.',
    'You finish what you started instead of stalling halfway':
        'Terminas lo que empezaste en vez de estancarte a la mitad',
    'The set he cuts today is why Thursday still has something in it. Fatigue gets spent where it buys you something.':
        'La serie que recorta hoy es la razón por la que el jueves todavía tiene algo dentro. La fatiga se gasta donde te compra algo.',
    'You keep training when something hurts': 'Sigues entrenando cuando algo duele',
    'Tell him and he removes what is unsafe, trains everything else at full effort, and brings the movement back on a ramp you can watch, in days you can count.':
        'Díselo y quita lo que no es seguro, entrena todo lo demás a esfuerzo completo, y trae el movimiento de vuelta en una rampa que puedes ver, en días que puedes contar.',
    'Day one against day one hundred': 'El día uno contra el día cien',
    'Most coaching apps are exactly as certain on your first session as your hundredth.':
        'La mayoría de las apps de coaching están igual de seguras en tu primera sesión que en la número cien.',
    'Only one of these two changes.': 'Solo una de estas dos cambia.',
    'A typical coaching app': 'Una app de coaching típica',
    'No basis shown. No confidence stated. No way to check it.':
        'Sin base mostrada. Sin confianza declarada. Sin forma de comprobarlo.',
    'unchanged since session 1': 'sin cambios desde la sesión 1',
    'I say so every time I do': 'lo digo cada vez que lo hago',
    'Basis: population research. Nothing here is a claim about your body. It becomes one only when your own sets say so.':
        'Base: investigación poblacional. Nada de esto es una afirmación sobre tu cuerpo. Lo será solo cuando tus propias series lo digan.',
    'Population': 'Población',
    'how it works': 'cómo funciona',
    'Not a mockup': 'No es una maqueta',
    'This is the actual screen. Read what it admits.':
        'Esta es la pantalla real. Lee lo que admite.',
    'It tells you it is still learning': 'Te dice que todavía está aprendiendo',
    'Every number carries where it came from': 'Cada número lleva de dónde vino',
    'Evidence moves it, and some of it holds a floor':
        'La evidencia lo mueve, y una parte sostiene un piso',
    'The seal': 'El sello',
    'Try to make him look better than he was.':
        'Intenta hacerlo ver mejor de lo que fue.',
    'A sealed prediction in the exact shape the app produces, field for field. Widen the range so he looks right, or change the lift. The fingerprint recomputes in your browser as you type.':
        'Una predicción sellada exactamente con la forma que produce la app, campo por campo. Ensancha el rango para que parezca acertado, o cambia el ejercicio. La huella se vuelve a calcular en tu navegador mientras escribes.',
    'VERIFIED': 'VERIFICADO',
    'Fingerprint, recomputed in your browser': 'Huella, recalculada en tu navegador',
    'matches the seal': 'coincide con el sello',
    'Nothing here is stored by us. The arithmetic ran on your machine.':
        'Nosotros no guardamos nada de esto. La aritmética corrió en tu máquina.',
    'Checking this page against the live verifier.':
        'Comprobando esta página contra el verificador en vivo.',
    'Where the category stops': 'Dónde se detiene la categoría',
    'Four kinds of app. One shared habit.': 'Cuatro tipos de app. Una costumbre compartida.',
    'They ask you a question, then ignore the answer.':
        'Te hacen una pregunta, y después ignoran la respuesta.',
    'A logbook': 'Una bitácora',
    'Records your sets beautifully. Decides nothing.':
        'Registra tus series con belleza. No decide nada.',
    'A plan': 'Un plan',
    'Adapts between sessions. Not during one.':
        'Se adapta entre sesiones. No durante una.',
    'A wearable': 'Un wearable',
    'Scores your recovery. Never writes your workout.':
        'Puntúa tu recuperación. Nunca escribe tu entrenamiento.',
    'A chatbot': 'Un chatbot',
    'Ask twice, get two answers. Nothing to hold it to next month.':
        'Pregunta dos veces y obtén dos respuestas. Nada a lo que atarlo el mes que viene.',
    'Decides your set, changes it as it lands, remembers you for months, and keeps score on himself where you can read it. You train, he adjusts, and you can check every call he made.':
        'Decide tu serie, la cambia mientras cae, te recuerda durante meses, y lleva la cuenta de sí mismo donde puedes leerla. Tú entrenas, él ajusta, y puedes revisar cada decisión que tomó.',
    'The pressure test': 'La prueba de presión',
    'Four things most apps never show you.':
        'Cuatro cosas que la mayoría de las apps nunca te muestran.',
    'What it knows': 'Lo que sabe',
    'What changed by a hundred': 'Lo que cambió a las cien',
    'What changes when you answer': 'Lo que cambia cuando respondes',
    'What it still needs': 'Lo que todavía necesita',
    'Every one of these was photographed automatically by our own test run, on a phone with nothing else on it. If a number here ever stops matching the app, the capture is the thing that is wrong.':
        'Cada una de estas fue fotografiada automáticamente por nuestra propia corrida de pruebas, en un teléfono sin nada más. Si algún número aquí deja de coincidir con la app, lo que está mal es la captura.',
    'I am Jeremiah Tachiwona, and I built this.':
        'Soy Jeremiah Tachiwona, y yo construí esto.',
    'Every coaching app I have paid for was certain about me on the first day, and not one of them ever came back and told me it had been wrong. That is the whole reason this one writes its guess down before you lift and then grades itself where you can read it.':
        'Cada app de coaching que he pagado estaba segura sobre mí el primer día, y ninguna volvió jamás a decirme que se había equivocado. Esa es toda la razón por la que esta anota lo que supone antes de que levantes y después se califica donde puedes leerlo.',
    'The commitment': 'El compromiso',
    'The accuracy record is published before we charge anyone.':
        'El registro de precisión se publica antes de cobrarle a nadie.',
    'Published once the number looks good, it is marketing. Published first, it is a commitment.':
        'Publicado cuando el número ya se ve bien, es publicidad. Publicado primero, es un compromiso.',
    '199 US dollars': '199 dólares',
    '14 days': '14 días',
    'A strength coach costs 200 to 400 US dollars a\n    month. This is 199 a year, and the accuracy record is published before anyone is charged.':
        'Un coach de fuerza cuesta entre 200 y 400 dólares al mes. Este cuesta 199 al año, y el\n    registro de precisión se publica antes de cobrarle a nadie.',
    'Email us': 'Escríbenos',
    'A real capture from the app, taken by the test suite on a clean install after one\n      logged session. Nothing retouched, nothing staged.':
        'Una captura real de la app, tomada por la suite de pruebas en una instalación limpia\n      después de una sesión registrada. Sin retoques, sin montaje.',
    'Photographed automatically by our own test run,\n      on a phone with nothing else on it.':
        'Fotografiada automáticamente por nuestra propia corrida de pruebas,\n      en un teléfono sin nada más.',
    'The same screen on day one, the same screen after a hundred logged\n    sessions, that screen again once the athlete answered one question, and the sheet behind it.\n    Each one admits something. Real captures from the test suite, nothing retouched. Where anything\n    was handed to the app rather than earned by it, the caption underneath says so.':
        'La misma pantalla el día uno, la misma pantalla después de cien sesiones registradas, esa\n    pantalla otra vez cuando el atleta respondió una pregunta, y la hoja que va detrás. Cada una\n    admite algo. Capturas reales de la suite de pruebas, sin retoques. Donde algo se le entregó a\n    la app en vez de que se lo ganara, el pie de foto lo dice.',
    'He changes your workout in the middle of it. Most apps hand you a program and stop listening.':
        'Te cambia el entrenamiento a la mitad. La mayoría de las apps te entregan un programa y dejan de escuchar.',
}


# ── /how-it-works/ ──────────────────────────────────────────────────────────────────────
HOWITWORKS = {
    'How it works · OrderedStrength': 'Cómo funciona · OrderedStrength',
    'The whole loop in plain English: how Jerry decides what you lift, reacts to each set, handles an injury, and refuses to guess when he cannot see enough.':
        'El ciclo completo en español simple: cómo decide Jerry qué levantas, cómo reacciona a cada serie, cómo maneja una lesión, y cómo se niega a adivinar cuando no alcanza a ver lo suficiente.',
    'One loop. You ask, you train, you rate each set, he reacts.':
        'Un solo ciclo. Pides, entrenas, calificas cada serie, él reacciona.',
    'Everything below is what the app actually does, written from its own source rather than from a brochure. Where it refuses to answer, that is a feature and it is described here too.':
        'Todo lo de abajo es lo que la app realmente hace, escrito desde su propio código y no desde un folleto. Donde se niega a responder, eso es una función y también se describe aquí.',
    'Day one is a deal, not a promise': 'El día uno es un trato, no una promesa',
    'Jerry asks your bodyweight, your experience, how many days a week you train, and your current lifts if you know them. Then he tells you plainly that on day one he has averages for someone your age, sex and weight, and nothing about you. He asks one thing in return: rate your effort honestly. Round up to look strong and he coaches a fake version of you.':
        'Jerry te pregunta tu peso corporal, tu experiencia, cuántos días a la semana entrenas, y tus marcas actuales si las sabes. Después te dice sin rodeos que el día uno tiene promedios de alguien de tu edad, sexo y peso, y nada sobre ti. Pide una sola cosa a cambio: que califiques tu esfuerzo con honestidad. Si lo inflas para verte fuerte, entrena a una versión falsa de ti.',
    'He builds the plan, then promises to grade it':
        'Arma el plan, y después promete calificarlo',
    'You get a multi-week plan and a first session, labelled for what it is: true for the average lifter like you, not yet true about you. Every call he makes about you gets graded, hits and misses alike.':
        'Recibes un plan de varias semanas y una primera sesión, etiquetada por lo que es: cierta para el levantador promedio como tú, todavía no cierta sobre ti. Cada decisión que toma sobre ti se califica, los aciertos y los fallos por igual.',
    'Three ways in': 'Tres formas de entrar',
    'Let him plan the whole session, pick the muscles you want, or freestyle and log whatever you do. If you pick muscles he does not simply obey: if a muscle still needs recovery, or your weekly workload is already high, he trims or declines it and shows a receipt explaining exactly why.':
        'Déjalo planear la sesión entera, elige los músculos que quieras, o entrena libre y registra lo que hagas. Si eliges músculos no obedece sin más: si un músculo todavía necesita recuperación, o tu carga semanal ya está alta, lo recorta o lo rechaza y muestra un comprobante explicando exactamente por qué.',
    'Rate each set, and he reacts before the next one':
        'Califica cada serie, y él reacciona antes de la siguiente',
    'After every set you say how many reps you had left. He compares that against what he expected and tells you in one line whether you are on track, drifting, or still teaching him your baseline on a new lift. If you are fading faster than planned he cuts the remaining sets on the spot and says that the cut protects your recovery.':
        'Después de cada serie dices cuántas repeticiones te quedaban. Él lo compara con lo que esperaba y te dice en una línea si vas bien, si te estás desviando, o si todavía le estás enseñando tu base en un ejercicio nuevo. Si estás cayendo más rápido de lo planeado, recorta las series restantes en el momento y dice que el recorte protege tu recuperación.',
    'The weight goes up when you have earned it': 'El peso sube cuando te lo ganaste',
    'Not on a calendar. He holds the load and asks for one more rep, then adds the plate once the reps are there. It runs on what you actually completed, not on how hard you said it felt.':
        'No por calendario. Mantiene la carga y pide una repetición más, y después agrega el disco cuando las repeticiones están. Funciona con lo que realmente completaste, no con lo duro que dijiste que se sintió.',
    'Tell him something and watch it land': 'Dile algo y observa cómo aterriza',
    'Report an injury and he names the lifts he just removed. Say a muscle is sore and he shows the effort buffer he added. Travel, get sick, change your equipment, and the plan changes with a receipt attached. If you quietly use a lighter weight than he asked for, he notices, and if you do it again on another day he lowers the prescription himself instead of arguing with you.':
        'Reporta una lesión y te nombra los ejercicios que acaba de quitar. Di que un músculo está adolorido y te muestra el margen de esfuerzo que agregó. Viaja, enférmate, cambia de equipo, y el plan cambia con un comprobante adjunto. Si usas en silencio un peso más ligero del que te pidió, se da cuenta, y si lo repites otro día baja él mismo la prescripción en vez de discutir contigo.',
    'It gets more personal over time': 'Se vuelve más personal con el tiempo',
    'Every number starts as an honest average. As you log real sets he shifts onto your own body and shows you how far he has moved and how sure he is. The pace follows your evidence: dense sessions of real working sets move him onto your numbers faster than the calendar does, and nothing opens because a week passed. Two of the deepest reads are the exception and hold a hard floor of fifteen sessions however hard you train, because below that the sample cannot mean anything. He says which, by name, on the screen where it matters.':
        'Cada número empieza como un promedio honesto. Conforme registras series reales, él se mueve hacia tu propio cuerpo y te muestra cuánto se ha movido y qué tan seguro está. El ritmo sigue tu evidencia: sesiones densas de series de trabajo reales lo mueven hacia tus números más rápido que el calendario, y nada se abre porque pasó una semana. Dos de las lecturas más profundas son la excepción y sostienen un piso duro de quince sesiones por muy duro que entrenes, porque debajo de eso la muestra no puede significar nada. Él dice cuáles, por su nombre, en la pantalla donde importa.',
    'Four moments': 'Cuatro momentos',
    'Where it stops feeling like an app.': 'Donde deja de sentirse como una app.',
    'Hard Truths': 'Verdades Duras',
    'When your own data shows a habit working against you, he says it out loud, using only your logged numbers. Before he speaks he rules out the innocent explanations: an injury, a beginner still learning, a planned easy week, a comeback. Each confrontation carries a receipt naming whose data, how much of it, and what he checked first. If he cannot rule out the innocent explanation he stays silent, because one false accusation costs trust permanently.':
        'Cuando tus propios datos muestran un hábito trabajando en tu contra, lo dice en voz alta, usando solo tus números registrados. Antes de hablar descarta las explicaciones inocentes: una lesión, un principiante que todavía aprende, una semana fácil planeada, un regreso. Cada confrontación lleva un comprobante que nombra los datos de quién, cuántos, y qué revisó primero. Si no puede descartar la explicación inocente se queda callado, porque una sola acusación falsa cuesta la confianza para siempre.',
    'The Teacher': 'El Maestro',
    'Instead of a generic tips feed, he teaches one principle at the exact moment your own training demonstrates it, and cites the research behind it. One thing at a time, never repeated, never invented. The lesson itself carries no numbers, because your numbers are in the receipt directly above it.':
        'En vez de un feed genérico de consejos, enseña un principio en el momento exacto en que tu propio entrenamiento lo demuestra, y cita la investigación detrás. Una cosa a la vez, nunca repetida, nunca inventada. La lección misma no lleva números, porque tus números están en el comprobante justo encima.',
    'The day you get hurt': 'El día que te lesionas',
    'This is where other apps go quiet. Tell him something hurts and he keeps coaching: removes what is unsafe, trains everything else, and brings the injured movement back on a gradual ramp. Pain above the clinical line holds the ramp where it is rather than letting the calendar advance it. The screen shows the honest number of days until full load, and it is the same number the engine is using.':
        'Aquí es donde otras apps se quedan calladas. Dile que algo duele y sigue entrenándote: quita lo que no es seguro, entrena todo lo demás, y trae el movimiento lesionado de vuelta en una rampa gradual. El dolor por encima de la línea clínica mantiene la rampa donde está en vez de dejar que el calendario la avance. La pantalla muestra el número honesto de días hasta carga completa, y es el mismo número que está usando el motor.',
    'The set he watched': 'La serie que miró',
    'Prop the phone up and he will watch a set. He counts your reps and measures how much your speed dropped from the first to the last, which is the clearest sign of how close you came to failure. Then he tells you what he saw and compares it against what you logged. He is not allowed to change your weight from it, and he says so.':
        'Apoya el teléfono y mirará una serie. Cuenta tus repeticiones y mide cuánto bajó tu velocidad de la primera a la última, que es la señal más clara de qué tan cerca del fallo llegaste. Después te dice lo que vio y lo compara con lo que registraste. No tiene permitido cambiar tu peso a partir de eso, y lo dice.',
    'On the screen': 'En la pantalla',
    'The number on the screen is the number the engine is using.':
        'El número en la pantalla es el número que está usando el motor.',
    'When you report pain, the ramp does not advance on a calendar. Pain above the clinical line holds it exactly where it is. There is no separate optimistic figure shown to keep you feeling good, because a comforting number you cannot act on is worse than a hard one you can.':
        'Cuando reportas dolor, la rampa no avanza por calendario. El dolor por encima de la línea clínica la mantiene exactamente donde está. No hay una cifra optimista aparte para que te sientas bien, porque un número reconfortante sobre el que no puedes actuar es peor que uno duro sobre el que sí.',
    'Every confrontation carries a receipt in the same style: whose data, how much of it, and what was ruled out before he said anything.':
        'Cada confrontación lleva un comprobante con el mismo formato: los datos de quién, cuántos, y qué se descartó antes de que dijera nada.',
    'Right knee': 'Rodilla derecha',
    'returning to load': 'volviendo a la carga',
    'days until full load': 'días hasta carga completa',
    'Squats are out. I am training everything else at full effort. You logged pain at 4 out of 10 on Tuesday, which holds the ramp where it is rather than advancing it.':
        'Las sentadillas quedan fuera. Estoy entrenando todo lo demás a esfuerzo completo. Registraste dolor de 4 sobre 10 el martes, lo que mantiene la rampa donde está en vez de avanzarla.',
    'Hard truth': 'Verdad dura',
    'Your legs have sat under the growth minimum for three weeks while your pressing runs full.':
        'Tus piernas llevan tres semanas por debajo del mínimo de crecimiento mientras tu press va a tope.',
    'The part that matters most': 'La parte que más importa',
    'He would rather refuse than guess.': 'Prefiere negarse antes que adivinar.',
    'Most coaching apps overclaim, and once you catch one overclaim you quietly discount everything else. This one inverts that: it flags every guess and owns every miss, so the confident claims actually carry weight.':
        'La mayoría de las apps de coaching prometen de más, y en cuanto le atrapas una exageración descuentas en silencio todo lo demás. Esta lo invierte: marca cada suposición y asume cada fallo, así que las afirmaciones seguras sí pesan.',
    'Your data': 'Tus datos',
    'Easy to leave, hard to replace.': 'Fácil de dejar, difícil de reemplazar.',
    'Your training is computed on your device by our own engines. Bring your history in from the big logging apps so switching does not mean starting at zero, and export the whole record as a single file whenever you want. Nothing is held hostage to keep you subscribed.':
        'Tu entrenamiento se calcula en tu dispositivo con nuestros propios motores. Trae tu historial desde las apps grandes de registro para que cambiarte no signifique empezar de cero, y exporta el registro completo como un solo archivo cuando quieras. Nada se retiene como rehén para mantenerte suscrito.',
    'Losing your history is one of the loudest complaints in this category, and making cancellation difficult is what gets an app called a scam. We would rather be the product that is easy to leave and hard to replace.':
        'Perder tu historial es una de las quejas más ruidosas de esta categoría, y poner difícil la cancelación es lo que hace que a una app le digan estafa. Preferimos ser el producto que es fácil de dejar y difícil de reemplazar.',
    'privacy policy': 'política de privacidad',
    'See it for yourself': 'Compruébalo tú mismo',
    'The claims on this page are checkable.':
        'Las afirmaciones de esta página se pueden comprobar.',
    'Not by trusting the page. By running the arithmetic.':
        'No confiando en la página. Corriendo la aritmética.',
    'Break a sealed prediction': 'Rompe una predicción sellada',
    'Read the record': 'Lee el registro',
}


# ── /app-privacy/ ───────────────────────────────────────────────────────────────────────
# The legal page. Translated with the most care of any on the site: the App Store links to
# this URL, and it is the page that must not overclaim in either language.
PRIVACY = {
    'Privacy Policy · OrderedStrength': 'Política de Privacidad · OrderedStrength',
    'What the OrderedStrength iPhone app stores on your device, the four things that can leave it, how to switch each one off, and the one that should not be there.':
        'Qué guarda la app OrderedStrength para iPhone en tu dispositivo, las cuatro cosas que pueden salir de él, cómo apagar cada una, y la que no debería estar ahí.',
    'OrderedStrength Privacy Policy': 'Política de Privacidad de OrderedStrength',
    'Last updated: 17 August 2026.': 'Última actualización: 17 de agosto de 2026.',
    'OrderedStrength iPhone app': 'app OrderedStrength para iPhone',
    'The short version': 'La versión corta',
    'Four things can leave your device, and one of them should not be there.':
        'Cuatro cosas pueden salir de tu dispositivo, y una de ellas no debería estar ahí.',
    'What stays on your device': 'Lo que se queda en tu dispositivo',
    'All of this is stored on your iPhone. Nothing here is sent to us except where point 4 below says otherwise:':
        'Todo esto se guarda en tu iPhone. Nada de esto se nos envía salvo donde el punto 4 de abajo diga lo contrario:',
    'Your name, age, bodyweight, height and sex, if you enter them.':
        'Tu nombre, edad, peso corporal, estatura y sexo, si los ingresas.',
    'This is the one currently affected by point 4.':
        'Esta es la que actualmente afecta el punto 4.',
    'Any injury you record, and how you said it felt.':
        'Cualquier lesión que registres, y cómo dijiste que se sintió.',
    'Everything the coach learns about you: your strength estimates, fatigue model, calibration and history.':
        'Todo lo que el coach aprende sobre ti: tus estimaciones de fuerza, tu modelo de fatiga, tu calibración y tu historial.',
    'If you delete the app, this goes with it. That is why the app offers a backup file you keep yourself.':
        'Si borras la app, esto se va con ella. Por eso la app ofrece un archivo de respaldo que guardas tú mismo.',
    'It is never transmitted to us or to anyone else.':
        'Nunca se nos transmite ni a nosotros ni a nadie más.',
    'The four things that can leave your device':
        'Las cuatro cosas que pueden salir de tu dispositivo',
    'Be aware:': 'Ten en cuenta:',
    "1. Jerry's voice &middot; on when the spoken coaching voice is on":
        '1. La voz de Jerry &middot; encendida cuando la voz hablada del coach está encendida',
    '2. Ask Jerry &middot; OFF unless you turn it on':
        '2. Pregúntale a Jerry &middot; APAGADO a menos que lo enciendas',
    '3. A daily usage summary &middot; on by default, and you can turn it off':
        '3. Un resumen diario de uso &middot; encendido por defecto, y puedes apagarlo',
    'Once a day the app can send a short summary so we can tell whether the app is actually helping people train. It is tied to a random identifier created on your device, never to your name, and it contains day-level values only:':
        'Una vez al día la app puede enviar un resumen corto para que podamos saber si la app realmente está ayudando a la gente a entrenar. Está ligado a un identificador aleatorio creado en tu dispositivo, nunca a tu nombre, y contiene solo valores a nivel de día:',
    'which days you opened the app, and which days you trained;':
        'qué días abriste la app, y qué días entrenaste;',
    'how far you got in setup, and how long it took to log a first set;':
        'hasta dónde llegaste en la configuración, y cuánto tardaste en registrar una primera serie;',
    'how many times the app crashed;': 'cuántas veces se cerró la app inesperadamente;',
    'which language you use.': 'qué idioma usas.',
    'It does not include your sets, your weights, your body data, or anything from Apple Health.':
        'No incluye tus series, tus pesos, tus datos corporales, ni nada de Apple Health.',
    '4. Your logged sets &middot; currently sent, and being removed':
        '4. Las series que registras &middot; actualmente se envían, y se están quitando',
    'When you finish a freestyle workout, the app currently sends each set you logged to our server: the exercise, the weight, the reps, and the reserve you reported. It is tied to a random identifier created on your device and never to your name, and it is not sold, shared or used to advertise to you.':
        'Cuando terminas un entrenamiento libre, la app actualmente envía a nuestro servidor cada serie que registraste: el ejercicio, el peso, las repeticiones, y la reserva que reportaste. Está ligado a un identificador aleatorio creado en tu dispositivo y nunca a tu nombre, y no se vende, no se comparte ni se usa para mostrarte publicidad.',
    'We are not defending this one.': 'Esta no la estamos defendiendo.',
    'What we never do': 'Lo que nunca hacemos',
    'No advertising, and no advertising networks.':
        'Sin publicidad, y sin redes de publicidad.',
    'No third-party analytics or tracking SDKs. There are none in the app.':
        'Sin analítica de terceros ni SDKs de rastreo. No hay ninguno en la app.',
    'No tracking you across other apps or websites, and no Advertising Identifier.':
        'Sin rastrearte a través de otras apps o sitios web, y sin Identificador de Publicidad.',
    'No selling or sharing your information with data brokers.':
        'Sin vender ni compartir tu información con corredores de datos.',
    'No account, so no email list, and no profile of you held on our side.':
        'Sin cuenta, así que sin lista de correos, y sin ningún perfil tuyo guardado de nuestro lado.',
    'Your controls': 'Tus controles',
    'Back up everything': 'Respaldar todo',
    'Delete all training data': 'Borrar todos los datos de entrenamiento',
    'Turn off usage sharing': 'Apagar el envío de uso',
    'Turn off Cloud Answers': 'Apagar las Respuestas en la Nube',
    'Revoke Apple Health access': 'Revocar el acceso a Apple Health',
    'Delete the app': 'Borrar la app',
    'Service providers': 'Proveedores de servicio',
    'Children': 'Menores',
    'OrderedStrength is a strength-training tool intended for adults. It is not directed at children under 13, and we do not knowingly collect information from them.':
        'OrderedStrength es una herramienta de entrenamiento de fuerza pensada para adultos. No está dirigida a menores de 13 años, y no recolectamos información de ellos a sabiendas.',
    'Changes': 'Cambios',
    "If what the app does with data changes, this page changes with it and the date above is updated. The page is written from the app's own source code so that it stays true rather than generic.":
        'Si lo que la app hace con los datos cambia, esta página cambia con ello y la fecha de arriba se actualiza. La página está escrita desde el propio código de la app para que siga siendo cierta en vez de genérica.',
    'Contact': 'Contacto',
}

# ── In-app navigation paths, rendered in <em> on the support and privacy pages ───────────
# 🔒 TRANSLATED AS WHOLE PATHS, NEVER WORD BY WORD. The chrome key 'Privacy' -> 'Privacidad'
# turned "Profile / Data & Privacy / Back Up Everything" into "Profile / Data & Privacidad /
# Back Up Everything": three English words, one Spanish, in a path a reader is meant to follow
# on a Spanish phone. Half a translation is worse than none, because it looks deliberate.
# Every label below is the app's own es wording from Localizable.xcstrings.
APP_PATHS = {
    'Profile / Data &amp; Privacy / Back Up Everything':
        'Perfil / Datos y privacidad / Respaldar Todo',
    'Profile / Data &amp; Privacy / Delete All Training Data':
        'Perfil / Datos y privacidad / Eliminar todos los datos de entrenamiento',
    'Profile / Data &amp; Privacy': 'Perfil / Datos y privacidad',
    # Exactly as the app capitalises it. Matching the product is the whole principle.
    'Restore from Backup': 'Restaurar desde respaldo',
    'Cloud Answers': 'Respuestas en la Nube',
    'text of the sentence Jerry is about to say':
        'el texto de la frase que Jerry está a punto de decir',
}
