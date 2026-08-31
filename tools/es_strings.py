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
    'Build': 'Compilación',
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
