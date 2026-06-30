-- =============================================================================
-- Svarupa — concepts + concept-descriptions data load
-- Auto-generated from documentation/dimensions_and_concepts/*.docx
-- Run AFTER 001_svarupa_dimensions_concepts.sql (schema + lookups).
--
-- svarupa_concepts:             one row per named construct of each dimension
-- svarupa_concept_descriptions: one row per (concept, pole) the source segments
--                               into balance / excess / deficiency.
-- =============================================================================
SET NAMES utf8mb4;

START TRANSACTION;

-- Replace any previously-seeded concepts for these dimensions (the example D8
-- seed in 001 included). Cascade removes their descriptions automatically.
DELETE FROM svarupa_concepts WHERE dimension_id IN (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18);

-- -----------------------------------------------------------------------------
-- D1 — Five Great Elements  (5 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (1, 'prithvi', 'Prithvī', NULL, 'The Structural Foundation', 'The earth element provides form, shape, structure, and stability to the physical body. The five aspects of prithvī in the body, as described by the Brahmavidya, are bone, muscle, skin, nādī (channels), and hair. Earth represents the solid state of matter and symbolizes permanence and rigidity. In the living body, the teeth, cells, and tissues also represent earth. Its chief property is roughness (Kharatwa), and its tanmātra is smell (Gandha)—hence, disorders of the ability to smell reflect an imbalance of the earth element.

When the earth element is appropriately dominant in a person’s constitution, they tend to be expressive, grounded, detail-oriented, and enthusiastic in communication. They are the ‘down-to-earth’ individuals who bring stability to any situation.', 1),
    (1, 'apas', 'Apas', NULL, 'The Binding Principle', 'Water is the liquid state of matter, characterized by fluidity and the vital quality of binding and cohesion. Its five aspects in the body are semen, the reproductive fluids, fat, urine, and saliva. Blood, lymph, plasma, and all digestive juices are expressions of the water element. Water carries energy throughout the body, removes wastes, regulates temperature, and transports hormones and disease-fighting cells.

Its chief sensory attribute is Rasa (taste), because the sense of taste depends upon water in the mouth. When the water element dominates a person’s temperament, they become great analysts—cautious, restrained, and skilled at going into deep detail. The water personality is one who purifies and clarifies, moving through complexity with patience and precision.', 2),
    (1, 'agni', 'Agni', NULL, 'The Transformative Intelligence', 'Fire controls digestion, metabolism, and corresponds to intelligence and perception. The five aspects of agni in the body are hunger, thirst, sleep, light (the capacity to see), and drowsiness. Fire provides the light necessary for perception itself—the eyes are the vehicles through which light is digested and visual experience takes place. Hence, disorders of visual perception are primarily those of the fire element.

In Indian culture, fire is personified as Agni Deva, a god with two faces riding on a fiery ram—symbolic of fire as both life-giver and life-taker. Without the fire burning within us, there is no life. But when uncontrolled, fire consumes everything. The biological fire, or Jatharagni, is the cornerstone of Ayurvedic therapeutics. When Agni is balanced, all bodily activities proceed smoothly. Its disturbance is the root cause of disease. The fire personality is one driven by the desire to control, decide, and get things done—consuming everything in their path like a flame.', 3),
    (1, 'vayu', 'Vāyu', NULL, 'The Principle of Motion', 'Air represents the capacity for motion and kinetic energy—all forces and the movements that arise from them. The five aspects of vāyu in the body are removing, walking, smelling, contraction, and inflation. In living beings, air is a major constituent of the motor and sensory nerve impulses, the movement of food through the gastrointestinal tract, and all joint movements.

The origin of air is Sparsha, the tanmātra of touch—and because of their intimate relationship, the skin is considered the associated sense organ, while the hands are the organ of action. Air is also related to the mind and the movement of information through the nervous system. In Hindu mythology, Vayu’s sons Hanuman and Bhima were known for their immense strength and big, devoted hearts. But when the element of air becomes erratic, one experiences aggravated Vata dosha, which provokes anxiety, confusion, and restlessness.', 4),
    (1, 'akasha', 'Ākāsha', NULL, 'The Field of Possibility', 'Ākāsha is the subtlest element, present in all the voids within the body—the nostrils, mouth, abdomen, thoracic cavity, and the spaces between cells. It is not empty space but ether—a subtle dimension of existence. As the yogic tradition clarifies: Akasha is ‘that which is,’ while space (kala) is ‘that which is not.’

The five aspects of ākāsha in the body according to the Brahmavidya are desire to have, desire to repel, shame, fear, and forgetfulness. Ether’s chief attribute is non-resistance (Apratighatatwa), and it is associated with expansion and vibration. The pores, channels, and all empty spaces through which nutrition reaches cells and waste products are excreted represent the space element. Its quality without form means we are often unaware of it, captivated as we are by the forms within it.', 5);

-- -----------------------------------------------------------------------------
-- D2 — Three Gunas  (3 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (2, 'sattva', 'Sattva', NULL, 'The Mode of Luminous Clarity', 'Sattva is purity, light, and knowledge. It is associated with balance, harmony, wisdom, serenity, and a positive disposition conducive to spiritual and psychological growth. When sattva is dominant, one experiences clarity of mind, inner peace, and a deep connection to one’s authentic self. Actions become selfless and are motivated by a desire to serve and uplift.

Core traits (from Mahābhārata & Bhagavad Gita): Jnāna (knowledge), Sukha (happiness), Kshama (forgiveness), Ārjava (simplicity), Satya (truth), Śraddhā (faith).

As the Gita states: “Among these, sattva, being pure, is illuminating and free from evil. It binds the soul through attachment to happiness and knowledge.” (14.6)', 1),
    (2, 'rajas', 'Rajas', NULL, 'The Mode of Passionate Activity', 'Rajas is the guna of passion, action, and restless energy. It drives the impulse to achieve, conquer, and create. While rajas can be a powerful force for progress, it is also associated with desire, ambition, egotism, and attachment to the fruits of action. When rajas is dominant, the mind is agitated, the senses heightened, and one is driven by constant need for external validation.

Core traits: Duhkha (suffering/discontent), Matsara (malice/envy), Nindā (blame), Rāga (passion/attachment).

The Gita warns: “Know that rajas is of the nature of passion, born of desire and attachment. It binds the embodied soul through attachment to action.” (14.7)', 2),
    (2, 'tamas', 'Tamas', NULL, 'The Mode of Inertial Darkness', 'Tamas is the guna of ignorance, darkness, and inertia. It manifests as delusion, laziness, negativity, and attachment to material comforts. When tamas prevails, one experiences a lack of clarity, confusion, and a deep sense of disconnection. There is stuckness, unmotivation, and resistance to change.

Core traits: Ajnāna (ignorance), Moha (delusion), Bhaya (fear).

The Gita describes: “But know that tamas, born of ignorance, deludes all embodied beings. It binds through negligence, laziness and sleep.” (14.8)', 3);

-- -----------------------------------------------------------------------------
-- D3 — Sixteen Faces of Mind  (19 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (3, 'sattva', 'Sattva', NULL, 'The Three Gunas as Qualities of Lived Experience', 'When Sattva predominates, a person’s lived experience is characterized by clarity, spaciousness, and an effortless ethical sense. Physically, there is a feeling of lightness and vitality—the body feels clean, well-ordered, and responsive. At the vital level, energy flows evenly; there is neither the frenetic restlessness of rajas nor the leaden heaviness of tamas. Emotionally, the sattvic person feels at ease with themselves and the world. Their predominant emotions are compassion, contentment, and a quiet joy that does not depend on external stimulation. Cognitively, the mind is lucid—perception is sharp, memory is reliable, and the capacity for discriminative wisdom (viveka) is strong. The sattvic person sees connections where others see fragments, and feels a natural moral impulse that arises not from obligation but from seeing the unity of all life.

Mathew’s psychological research characterizes Sattva as “stability”—stress tolerance, freedom from fear and maladjustment tendencies, present-centeredness, egolessness. Persons with high Sattva are wise, holistic, altruistic, full of love and compassion, transcending and broad-minded. They have a natural moral sense based on mature love, with a well-integrated personality capable of functioning differently in different situations while maintaining complete self-control and awareness.', 1),
    (3, 'rajas', 'Rajas', NULL, 'The Three Gunas as Qualities of Lived Experience', 'When Rajas predominates, life feels urgent, driven, and often agitated. Physically, the rajasic person may experience inflammation, heat, and tension—the body is always in motion, often overworked and under-rested. At the vital level, energy comes in surges and crashes: there is great capacity for action, but it is rarely sustained evenly. Emotionally, the rajasic landscape is dominated by desire, frustration, competitiveness, and a possessive quality to love. The predominant emotions are anger, passion, and a hunger for recognition and achievement that is never fully satisfied. Cognitively, the mind is sharp and analytical but restless—good at planning and strategizing, but prone to mood swings and difficulty with sustained contemplation.

Mathew defines Rajas as “activation”—extraverted instability, proneness to development of extraverted types of maladjustment under stress. The cause of activation is compensatory aggressiveness; the predominant emotions are anger, passion, and possessive love. People with high activation are impatient, hasty, risk-taking, rash, adventurous, analytical, efficient in planning, competitive, assertive, aggressive, dominant, proud, rebellious, greedy, and egoistic with an internal locus of control. Their mind is more integrated than the tamasic type, but they experience significant mood swings.', 2),
    (3, 'tamas', 'Tamas', NULL, 'The Three Gunas as Qualities of Lived Experience', 'When Tamas predominates, the experience of life is one of heaviness, obscurity, and resistance. Physically, the tamasic person feels sluggish, heavy, and often fatigued—the body seems to resist movement. At the vital level, energy is low and stagnant; there is little impetus toward action or change. Emotionally, the tamasic landscape is marked by fear, apathy, and a vague sense of dissatisfaction that cannot quite be articulated. The predominant emotion is fear—not the sharp fear of an immediate threat, but a pervasive background anxiety that saps initiative. Cognitively, the mind is dull, slow to process, prone to confusion, and resistant to learning. Memory is poor, attention wanders, and the capacity for self-reflection is severely limited.

Mathew defines Tamas as “inertia”—introverted instability, proneness to development of introverted types of maladjustment under stress, due to behavioural inhibition. The root cause is fear. The characteristics include lethargy, anxiety, low initiative, low self-confidence, low self-respect, and an external locus of control. Tamasic individuals have the least awareness, are susceptible to dissociation, and have the least control over their minds.', 3),
    (3, 'brahma_sattva', 'Brahma Sattva', NULL, 'The Seven Sattvic Archetypes', 'Named after Brahmā, the Creator: pure consciousness reflecting on its own nature

The Brahma-sattvic individual lives from the deepest possible centre. Their inner experience is one of quiet luminosity—a mind that naturally rests in clarity the way water rests in stillness. They possess profound spiritual knowledge (Jnāna and Vijnāna), an excellent memory, and an extraordinary power of discrimination. They are capable of scientific, philosophical, and religious discourse with equal facility, because for them these are not separate domains but facets of a single truth.

Emotionally, they are free from desire, anger, greed, conceit, infatuation, envy, dejection, and intolerance. This is not the coldness of repression but the warmth of a love so vast that it extends impartially to all beings—seeing divinity in every form of life. They observe fasts and rituals not from obligation but from a natural attunement to the sacred rhythms of existence.

In lived experience, the Brahma type is the person in any community who seems to carry an inner stillness that others instinctively trust. They are the natural counsellor, the person whose presence calms a room. Their suffering, when it arises, tends to come not from personal desire but from witnessing the suffering of others—a compassionate ache that motivates them toward service rather than withdrawal.', 4),
    (3, 'rishi_sattva', 'Rishi Sattva', NULL, 'The Seven Sattvic Archetypes', 'Named after the Rishis, the ancient seers: knowledge pursued as sacred duty

The Rishi-sattvic individual experiences life as a vocation of study and devotion. Their inner world is one of disciplined focus—the mind naturally inclines toward learning, ritual, and the pursuit of truth through sustained intellectual effort. They are endowed with keen perception and an understanding of scientific truth; their memory is sharp, and they are eloquent speakers who can articulate complex ideas with precision and beauty.

They are devoted to sacrifice, study, vows, and spiritual practices; celibacy often comes naturally to them—not as suppression but as a channelling of vital energy toward higher pursuits. They are hospitable, devoid of pride, conceit, attachment, hate, infatuation, greed, and anger. Their humility is not performed but genuine: they are so absorbed in their pursuit of knowledge that self-promotion feels irrelevant.

In lived experience, the Rishi type is the scholar-practitioner whose depth of learning inspires awe, yet whose personal manner is warm and unpretentious. They are often found in academic, monastic, or research settings—any environment where sustained inquiry is valued. Their challenge is that their devotion to study can sometimes create a distance from the messy, passionate dimensions of ordinary life.', 5),
    (3, 'aindra_sattva', 'Aindra Sattva', NULL, 'The Seven Sattvic Archetypes', 'Named after Indra, King of the Devas: leadership rooted in ethical authority

The Aindra-sattvic individual experiences life through the lens of stewardship and responsibility. Their inner world is one of strategic clarity—they naturally perceive the dynamics of groups, institutions, and systems, and feel called to organize and lead them toward their highest potential. They are intelligent, strategic, and capable of long-term planning. They are efficient decision-makers and command respect naturally, not through coercion but through the evident quality of their judgment.

They possess a strong physical and psychological presence and are brave—willing to face difficult situations and make hard decisions. They manage resources and people effectively, using their power for both personal fulfilment and the welfare of their followers and community. They are authoritative in speech and can inspire large groups toward a common purpose.

In lived experience, the Aindra type is the natural leader who is found heading organizations, communities, or movements. Their challenge is the temptation of power—when the sattvic quality dims, the authority that once served others can become self-serving. At their best, they embody the Vedic ideal of the just ruler: firm, wise, and dedicated to the welfare of all.', 6),
    (3, 'yama_sattva', 'Yama Sattva', NULL, 'The Seven Sattvic Archetypes', 'Named after Yama, Lord of Dharma: unwavering adherence to principle

The Yama-sattvic individual experiences life as a matter of principle. Their inner world is ordered, structured, and governed by a powerful moral compass. They are strong-willed, intelligent, and focused on single-minded goals. They follow their aims with a determination that others may find intimidating, yet they are not aggressive—merely unshakeable. They exhibit patience and are free from excessive hatred or envy.

They are highly moral and abide strictly by laws and principles—not out of fear of punishment but from a deep conviction that right action is its own reward. They are independent, non-quarrelsome, and often solitary by preference. They do not seek social validation and are comfortable making decisions that others may not understand or support.

In lived experience, the Yama type is the principled individual who stands firm when others waver—the judge, the ethicist, the monk who maintains a vow for decades. Their challenge is the risk of rigidity: when the sattvic quality becomes too concentrated in structure, it can lose the warmth of compassion and become a cold, unyielding legalism.', 7),
    (3, 'varuna_sattva', 'Varuna Sattva', NULL, 'The Seven Sattvic Archetypes', 'Named after Varuna, Lord of Cosmic Order: truth spoken with grace

The Varuna-sattvic individual experiences life as an arena for truth and justice, expressed with eloquence and composure. Their inner world is characterized by emotional balance—they are gifted speakers who can maintain composure in the most difficult situations, yet they are not cold. They exhibit controlled emotions, displaying appropriate anger or pleasure when the situation demands it, and they fight passionately for the right causes.

They are inherently pure and clean, disliking messiness, disorder, or chaotic environments—not from fastidiousness but from a deep alignment with cosmic order (Rita). They are deeply spiritual and honest, and their speech carries a natural authority because it is rooted in truthfulness rather than manipulation.

In lived experience, the Varuna type is the advocate, the diplomat, the spiritual teacher whose words carry weight because they emerge from integrity. They are found in settings where truth must be articulated under pressure—courtrooms, negotiation tables, podiums. Their challenge is that their commitment to order can sometimes make them intolerant of the creative chaos that is also a part of life.', 8),
    (3, 'kubera_sattva', 'Kubera Sattva', NULL, 'The Seven Sattvic Archetypes', 'Named after Kubera, Lord of Wealth: abundance pursued and shared

The Kubera-sattvic individual experiences life through the lens of abundance—not merely material wealth, but the richness of social connection, intellectual engagement, and generous exchange. They possess shrewd intelligence directed toward acquiring and managing resources, and they enjoy debate and intellectual discussion. They pursue wealth acquisition with passion, yet they do so with a consciousness of self-dignity and ethical boundary.

They are courageous and patient, enjoying a rich social life surrounded by family and friends. They are socially extroverted and generous with their wealth, using it to support others and to create environments of beauty and comfort. They maintain their self-dignity without arrogance, understanding that true wealth includes the quality of one’s relationships.

In lived experience, the Kubera type is the philanthropist, the successful entrepreneur who builds communities, the host whose home is always open. Their challenge is the boundary between sattvic generosity and rajasic acquisitiveness—when the drive to accumulate overshadows the impulse to share, the Kubera type slides toward the rajasic spectrum.', 9),
    (3, 'gandharva_sattva', 'Gandharva Sattva', NULL, 'The Seven Sattvic Archetypes', 'Named after the Gandharvas, celestial musicians: beauty as a path to the divine

The Gandharva-sattvic individual experiences life as an aesthetic and sensory celebration. Their inner world is one of refined sensitivity—they perceive beauty in form, sound, colour, and movement that others might overlook. They are talented in the creative arts: music, dance, poetry, and visual expression come naturally to them. They have a sophisticated and elegant sense of style.

They are prone to enjoying life’s pleasures in a refined manner—they can be sensual, but they often channel their vitality into creative expression and charming social interactions rather than mere indulgence. Their physical beauty and grace are often remarked upon, but it is their aesthetic intelligence that truly distinguishes them.

In lived experience, the Gandharva type is the artist, the dancer, the musician, the designer whose work elevates the experience of those around them. Their challenge is the thin line between sattvic aesthetic refinement and rajasic sensual indulgence—when pleasure becomes the primary motivation rather than the natural by-product of creative expression, the Gandharva type risks losing their luminous quality.', 10),
    (3, 'asura_rajasika', 'Asura Rajasika', NULL, 'The Six Rajasic Archetypes', 'Named after the Asuras, the power-seeking anti-gods: strength without surrender

The Asura-rajasic individual experiences life as a contest of wills. Their inner world is one of relentless ambition—they possess strong will and determination, and they are often shrewd and intelligent, capable of sophisticated strategy. But their intelligence is harnessed to the project of dominance rather than harmony. They are assertive, dominant, and proud; they pursue their goals aggressively and seek power and recognition above all else.

Emotionally, they are prone to envy and self-praise. They are tough taskmasters who push themselves and others hard, often achieving impressive external results at the cost of inner peace and genuine human connection. They can be deceptive when it serves their purposes, and their charm often masks a calculating quality.

In lived experience, the Asura type is the ruthless competitor, the domineering executive, the person whose presence generates both admiration and fear. Their suffering is the suffering of perpetual dissatisfaction: no achievement is ever enough, no victory is ever final, and beneath the confident exterior there is often a deep insecurity that fuels the drive for more. The path toward balance involves redirecting their formidable energy from conquest to contribution—learning that true power lies in service rather than domination.', 11),
    (3, 'rakshasa_rajasika', 'Rakshasa Rajasika', NULL, 'The Six Rajasic Archetypes', 'Named after the Rakshasas, fierce beings of myth: raw power unleashed without restraint

The Rakshasa-rajasic individual experiences life with an intensity that can be both terrifying and compelling. Their inner world is one of surging emotional force—anger, desire, and appetite are felt with overwhelming power. They have high levels of energy that can quickly turn aggressive or cruel. They are intolerant, deceitful, and fond of strong sensory experiences including non-vegetarian food and addictive substances.

They are highly irritable, prone to violence, and their actions are driven by intense desires and a fundamental lack of self-control. Their relationships are often stormy and marked by cycles of passion and conflict. They may be physically imposing and present a formidable, assertive presence.

In lived experience, the Rakshasa type is the person whose rages terrify others, whose appetites seem bottomless, and whose life is a series of dramatic escalations and crises. Their suffering is the suffering of a fire that consumes its own fuel: the intensity that makes them powerful also makes them destructive, both to others and to themselves. The path toward balance involves learning to channel their extraordinary energy through discipline—martial arts, structured physical practice, or service in environments where intensity is an asset rather than a liability.', 12),
    (3, 'paishacha_rajasika', 'Paishacha Rajasika', NULL, 'The Six Rajasic Archetypes', 'Named after the Pishāchas, beings of the shadow: appetite unchecked by awareness

The Paishacha-rajasic individual experiences life through the lens of appetite and compulsion. Their inner world is dominated by hunger—not just for food, but for sensory experience in all its forms. They are gluttonous, with a ravenous quality to their desires. They may live in luxury yet feel perpetually unsatisfied. They love company but often keep it in secret, and may struggle with secretive indulgences.

They may show a lack of engagement in mental or intellectual activities and a tendency toward disregard for cleanliness and social norms. They may prefer isolation and struggle with self-regulation—the boundary between enough and too much is perpetually blurred.

In lived experience, the Paishacha type is the person caught in cycles of bingeing and withdrawal—whether with food, substances, relationships, or experiences. Their suffering is the suffering of a void that cannot be filled from the outside. The path toward balance involves learning to turn awareness inward—to recognize that the hunger is not for more stimulation but for a quality of presence that can only be found through stillness and self-knowledge.', 13),
    (3, 'sarpa_rajasika', 'Sarpa Rajasika', NULL, 'The Six Rajasic Archetypes', 'Named after the Sarpa (serpent): watchful, coiled, and unpredictable

The Sarpa-rajasic individual experiences life as a landscape of threat and opportunity. Their inner world is one of watchful tension—quick-witted but prone to anxiety and apprehension. They are usually indolent, yet become heroic in anger; timid in daily life but capable of sudden, intense aggression when they feel cornered. They are expert at counselling others but often use indirect means, trickery, or deceit to achieve their own aims.

They have strong habits and are given to the pleasures of the senses, yet there is always a cautious, calculating quality to their indulgence. Their actions are often unpredictable, blending fear with cunning in a way that keeps others off balance.

In lived experience, the Sarpa type is the person who is difficult to read—charming and helpful one moment, sharp and vengeful the next. Their suffering is the suffering of chronic vigilance: because they see the world as threatening, they can never fully relax, and their relationships are often undermined by the very suspicion and manipulation that they believe protects them. The path toward balance involves cultivating trust—learning, slowly, that not every situation demands a defensive posture, and that vulnerability is not the same as weakness.', 14),
    (3, 'preta_rajasika', 'Preta Rajasika', NULL, 'The Six Rajasic Archetypes', 'Named after the Pretas, spirits of insatiable craving: desire without fulfilment

The Preta-rajasic individual experiences life through a lens of chronic dissatisfaction and craving. Their inner world is marked by greed, irritability, and a pervasive sense of dejection. They love food and are deeply attached to material comforts, yet they are disinclined to work—the gap between desire and effort creates a perpetual frustration. They have no power of discrimination and are extremely jealous.

Their conduct, character, and pastimes are such as to involve others in suffering. They may harbour personal vendettas or spread hatred, driven by a sense of having been denied what they deserve. There is a fundamentally acquisitive quality to their engagement with the world, yet no acquisition brings lasting satisfaction.

In lived experience, the Preta type is the chronically dissatisfied person—the one who complains that others have what they deserve, who hoards yet feels impoverished, who desires yet resents the effort required to obtain. Their suffering is the suffering of the hungry ghost: surrounded by abundance yet unable to receive nourishment. The path toward balance involves the practice of gratitude and generosity—the deliberate cultivation of satisfaction with what one has, and the discovery that giving is the most effective cure for the feeling of lack.', 15),
    (3, 'shakuni_rajasika', 'Shakuni Rajasika', NULL, 'The Six Rajasic Archetypes', 'Named after the Shakuni (bird): always in flight, never settled

The Shakuni-rajasic individual experiences life as a constant search for the next stimulation. Their inner world is one of fickleness and restless movement—they are always seeking food, recreation, and new experiences, but their attention never rests on anything for long. They are passionate but intolerant, incapable of sustained remunerative work, suspicious of others, and prone to strong attachments that form quickly and dissolve just as fast.

They have strong sexual desires and a tendency toward excessive indulgence, yet their relationship with pleasure is characterized by variability—they are easily distracted by the next possibility before the current one has been fully experienced. They are unacquisitive in the long term because they lack the sustained attention needed for accumulation.

In lived experience, the Shakuni type is the person who flits from interest to interest, relationship to relationship, plan to plan—leaving a trail of unfinished projects and unfulfilled promises. Their suffering is the suffering of scattering: because attention is always divided, no experience is ever fully received, and the deep satisfaction that comes from sustained engagement remains elusive. The path toward balance involves the practice of concentration—learning to rest attention on one thing, one person, one purpose long enough for depth to emerge.', 16),
    (3, 'pashu_tamasa', 'Pashu Tamasa', NULL, 'The Three Tamasic Archetypes', 'Named after Pashu (animal): instinctive existence, unreflective and passive

The Pashu-tamasic individual experiences life at the level of basic instinct and routine. Their inner world is one of dullness, absence of sustained reflection, and passivity. They are mentally deficient in terms of intellectual engagement—not necessarily incapable, but deeply resistant to the effort that thinking requires. They are absent-minded, slow-moving, timid, foolish, and lazy. They are dirty in dress and ignorant in their dealings.

They are given to eating, drinking, and sensuality—not with the passionate intensity of the rajasic types, but with the mechanical quality of an animal satisfying a drive. They are sleepy and prone to rejecting everything—new ideas, new people, new experiences. Their default response to the world is withdrawal and resistance.

In lived experience, the Pashu type is the person who seems to exist rather than live—going through motions without engagement, responding to the world with the minimum possible effort. Their suffering is the suffering of unconsciousness: they are unable to articulate what is wrong because self-awareness itself is the faculty that tamas most effectively suppresses. The path toward balance begins with simple physical activity—movement, routine, the creation of basic structure—which introduces just enough rajas to begin loosening the grip of inertia.', 17),
    (3, 'matsya_tamasa', 'Matsya Tamasa', NULL, 'The Three Tamasic Archetypes', 'Named after Matsya (fish): restless motion without direction or understanding

The Matsya-tamasic individual experiences life as a kind of frightened restlessness—they are driven by instinctual urges but lack the cognitive resources to make sense of or direct their movement. They are mentally deficient, cowardly, prone to stupidity, gluttonous, fickle, and susceptible to anger and sensuality in rapid alternation. They love to travel and are drawn to water—a restless quality that is often mistaken for rajasic activity but is actually a tamasic flailing without purpose.

Their inner world is marked by apprehension and a reactive quality: they respond to stimuli not with understanding but with reflex. Their engagement with the world is primarily driven by the most basic needs—hunger, fear, and the pursuit of immediate sensory comfort.

In lived experience, the Matsya type is the person who is always moving but never arriving—changing jobs, changing cities, changing partners, but always carrying the same confusion and restlessness with them. Their suffering is the suffering of disorientation: they lack the inner compass that would allow them to distinguish meaningful action from mere agitation. The path toward balance involves grounding—establishing stability in one place, one relationship, one practice—long enough for the turbid waters of the mind to begin to settle.', 18),
    (3, 'vanaspati_tamasa', 'Vanaspati Tamasa', NULL, 'The Three Tamasic Archetypes', 'Named after Vanaspati (plant): existence without volition or awareness

The Vanaspati-tamasic individual represents the deepest level of tamasic experience. Their inner world is one of near-total absence of mental activity—extreme laziness, complete indifference to surroundings, and minimal engagement with the world. They spend most of their time eating and sleeping. They are completely devoid of all mental faculties as traditionally defined—lacking initiative, curiosity, ambition, and even the restless agitation that still animates the Pashu and Matsya types.

They show the lowest level of mental activity and significant indifference to everything around them. Psychologically, they are characterized by extreme passivity, a complete lack of initiative, and a mode of existence that resembles a static form of life.

In lived experience, the Vanaspati type is the person who has essentially withdrawn from participation in life—not through the active choice of a contemplative, but through the weight of inertia that has compressed awareness to its minimal expression. Their suffering is invisible even to themselves because the capacity for self-reflection that would allow them to recognize suffering has been almost entirely suppressed. The path toward balance is the longest and most difficult of all the types, requiring external intervention: compassionate others who introduce stimulation, structure, and care—the first rays of light entering a room that has been dark for a very long time.', 19);

-- -----------------------------------------------------------------------------
-- D4 — Seven Layers of Consciousness  (7 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (4, 'the_waking_state', 'The Waking State', NULL, 'The World of Sensory Perception', 'The waking state of consciousness is the consciousness of the five senses. It is the plane of perception: we see, we hear, we touch, we taste, we smell. It is here that the vast majority of human beings spend the vast majority of their lives. The teachings describe it as the plane of “my body, my house, my wealth, my work.” It is the domain of identification with the physical and the material, the plane where the self is experienced as coterminous with the body and its possessions.

When a person’s consciousness is predominantly anchored in the waking plane, their lived experience is characterised by several distinctive qualities. First, reality is defined entirely by sensory input. What can be seen, measured, and touched is real; what cannot is dismissed or ignored. Second, the sense of self is bound to external identity markers—name, profession, social role, physical appearance, material assets. Third, emotional life is largely reactive: happiness arises when sensory conditions are favorable, suffering when they are not. There is very little inner space between stimulus and response.

The elemental disturbances described in the Ayurvedic and Yogic traditions are experienced most acutely at this level. When fire is in excess, the person at the waking plane is entirely consumed by irritability, inflammation, and competitive rage—there is no vantage point from which to witness these states. When air is disturbed, anxiety scatters the mind and the person feels helpless before it. When earth predominates, heaviness and inertia feel like the whole of reality. The person at this plane has no tools for disidentification. They are what they feel, fully and without remainder.

The waking consciousness is also where the five constituent elements of the human frame—body, mind, intellect, ego, and soul—are experienced primarily through the first and most gross element alone: the body. The being, the soul, the fifth element, is present but buried beneath the four coverings of body, mind, intellect, and ego. At this plane, a person is alive but not yet truly awake to what lies within.

•  •  •', 1),
    (4, 'the_dreaming_state', 'The Dreaming State', NULL, 'The World of Samskāras', 'The second layer of material consciousness is the dreaming plane. The teachings describe it as the consciousness of samskāras—that which is stored up from previous lives and from the accumulated impressions of this one. While the waking plane corresponds to the gross body and its sensory apparatus, the dreaming plane corresponds to the subtle body and its storehouse of latent impressions.

In the ordinary dreaming state, the consciousness replays and recombines the material of waking experience. When a person fights with their neighbour in a dream, runs out of fear, or eats when hungry, this is dreaming of the material plane—the second layer processing the first. But there is a critical distinction the teachings make: sometimes, even in the dream state, content arises that has nothing to do with the earth plane or earth consciousness. Visions from different planes may appear. When they do, they are not called dreams but revelations. This indicates that even within the ordinary structure of sleep, there are moments when consciousness touches something beyond the material.

For a person whose consciousness is habitually situated in the dreaming layer (in a functional, not literal sense), lived experience is colored heavily by the past. Such a person is less reactive to immediate sensory events than the person anchored in waking consciousness, but they are deeply conditioned by accumulated patterns—habitual emotional responses, relational dynamics that repeat across different relationships, inherited fears and desires that feel inexplicable in terms of present-life circumstances. The weight of samskaric material shapes perception, creating a kind of filter through which all present experience is interpreted. This person may appear thoughtful or introspective but is often caught in loops of memory, fantasy, and unconscious repetition.

The ancient analysis of matter recognized that in subtle matter, the forms consciousness assumes are freer and more rapid, but also more volatile, elastic, and swiftly mutable. This is precisely the quality of dream-life and of the inner experience of a person dominated by their samskaric conditioning: everything moves quickly, shifts shape, and lacks the stability of waking perception, yet also lacks the limitation of being tied to immediate physical facts.

•  •  •', 2),
    (4, 'the_sleeping_state', 'The Sleeping State', NULL, 'The World of the Psychic', 'The third layer of material consciousness is the sleeping plane, and here the teachings reveal something unexpected. Sound sleep, dreamless sleep, is not unconsciousness. It is what the tradition calls the consciousness of Samādhi. The consciousness is present during sleep, but it is so subtle that the mind cannot catch it. It is subtler than mind. Sound sleep and samādhi have very little difference. Sound sleep is described as a small death; death is nothing but a long sound sleep.

In this state, the consciousness touches what the teachings call the psychic plane—the domain of the soul element within the human frame. When dreamless sleep is truly deep and undisturbed, what is experienced is not the world of perception (waking) or the world of samskāras (dreaming), but a kind of pure blissful existence. The ancient seers called this the Sleep State and found that in causal matter, consciousness took the shape merely of the pure sense of blissful existence; they could discover no other distinguishing sensation.

Very few people have awareness in the sleeping state of consciousness. This means that the deepest layer of the material plane—the one closest to the spiritual domain—is for most human beings entirely unconscious. Yet it shapes lived experience profoundly. The quality of a person’s sleep, the degree to which they emerge from sleep feeling renewed or depleted, the rare and luminous quality of certain nights where one wakes feeling touched by something beyond the ordinary—all of this relates to the sleeping plane. Those yogis who have developed awareness even in deep sleep report a qualitative transformation: they need far less sleep, yet feel vastly more fulfilled. Half an hour of sleep gives more vitality than seven or eight hours of ordinary sleep. This is the first indicator that consciousness is beginning to transcend the material planes.', 3),
    (4, 'the_transcendental_state', 'The Transcendental State', NULL, 'The Bridge Between Matter and Spirit', 'If there is a single teaching that emerges from all the source texts with overwhelming emphasis, it is the centrality of the transcendental plane. The fourth layer of consciousness is the link between the consciousness in the material plane and the consciousness in the spirit plane. It is the transcendental that makes matter meaningful and spirit so important. Without the transcendental, matter would be dead, inconscient. Without the transcendental, spirit would be abstract and meaningless.

The teachings state with extraordinary directness: the key to rapid progress lies in the expansion of the transcendental. Not in the waking plane, not in the dreaming plane, not in the sleeping plane, and—remarkably—not directly in the God, Unity, or Cosmic planes either, because those higher planes can play their role only through the transcendental. Everything pivots here.

How the transcendental is reached. Remaining in the waking plane, when a person aspires to ascend, the force of that aspiration pushes consciousness toward the transcendental plane. But the transcendental cannot be reached without passing through the dreaming and sleeping layers. This is why the practices of yoga, meditation, and sādhanā inevitably surface dream content, disturb sleep patterns, and bring hidden material to the surface. The aspirant must pass through the accumulated impressions of the dreaming plane and the deep psychic territory of the sleeping plane before breaking through to the transcendental.

The experience of falling back. In the early stages, the seeker cannot remain in the transcendental. Upon entering it, they fall back to the waking plane, but they bring with them a little of the transcendental consciousness. This happens repeatedly. Each ascent deposits a residue of the higher consciousness in the lower planes. Gradually, waking life begins to be colored by transcendental quality: the person experiences transcendental waking (aware but not so identified with awareness), transcendental dreaming (visions rather than mere replays of sensory life, movement with angels and gods rather than fights with neighbors), and transcendental sleeping (sleep that is much reduced but deeply fulfilling).

These three experiences—transcendental waking, transcendental dreaming, and transcendental sleeping—are described as direct proof that a person is making progress on the path. And conversely, if these experiences do not arrive within a reasonable period of sincere practice, the tradition holds that the time for the spiritual path may not yet have come, and the person’s development should focus on expansion within the material realm.

The transformation of lived experience. For the person whose consciousness begins to stabilize in the transcendental, the quality of daily life undergoes a profound shift. They are still in the world—going to market, arguing in court, eating dinner—but their consciousness is no longer fully captured by these activities. There is an inner witness that persists. The teachings use the metaphor of a skilled driver navigating crowded streets: he is not looking at anyone specifically, but he sees everyone. He is careful, alert, yet not consumed by any single stimulus.

The practical consequences are remarkable. As long as one is able to remain in the fourth plane of consciousness, many diseases will not affect the person. Ninety percent of sickness comes from germs, bacteria, and viruses that operate at the earth-plane wavelength. When consciousness rises above this wavelength, the body becomes less susceptible to their influence. This is offered not as magical thinking but as an explanation for the well-documented phenomenon of saints and seers remaining healthy in environments that devastate others—in epidemic zones, in extreme cold with bare bodies, in conditions that would ordinarily destroy the physical frame. The consciousness, when established beyond body and mind, simply does not register the physical plane’s disturbances with the same force.

The transcendental is also described as the psychic realm—the plane of the soul. When the being within, long buried under the coverings of body, mind, intellect, and ego, begins to reassert itself, it first recaptures the mental plane, then the vital, then the physical. This reassertion of the being across all planes of the human frame is what constitutes genuine spiritual awakening, and it proceeds through and from the transcendental.', 4),
    (4, 'god_consciousness', 'God Consciousness', NULL, 'The Experience of Supreme Love', 'God consciousness is defined in these teachings not as an intellectual concept but as a concept of direct experience. It is described as the simultaneous experience of sat (being) and chit (consciousness) in their totality. While the transcendental plane allows one to witness, and the state of the Ātman (the Being) allows one to rest in pure awareness, God consciousness adds a dimension that neither of these states possesses: love. In the state of the Being there is no love—it is simply witnessing. Love comes beyond Being, and love comes from God.

For the person who begins to receive flashes of God consciousness, the lived experience is characterized by a flow of devotion that is qualitatively unlike any ordinary emotion. It does not depend on mutual exchange. The teachings describe this with remarkable precision: you do not share food, shelter, emotions, or whims with the object of this devotion, and yet the love flows. It is unilateral, uncaused, and overwhelming. This is because through the experience of God consciousness, one is getting the rare opportunity of experiencing chit and sat at the same time—a unitary experience that ordinary relationships, which are always bilateral and conditional, can never provide.

The person in this state may fluctuate wildly between exalted experiences and ordinary mundane concerns. One moment, the awareness arises: I am Brahman, I am Divine, I am He. The next moment, anxiety about tomorrow’s meal returns. The teachings insist that both experiences are genuine. The exalted state is not hypocrisy or fantasy; it is a real flash of a higher plane. But the person cannot hold it, because to hold it, the vital must be transparent, the mind must be still, and the physical must be strong. When any or all of these conditions are lacking, the experience fades.

Those who have not undergone this process may judge the person as unstable or self-deluding. But the tradition recognizes this oscillation as a natural and necessary part of the journey. The process proceeds through repeated flashes in which the finite within is expanding as the infinite. Each flash, though temporary, leaves behind an awareness that gradually becomes the background of all experience.

•  •  •', 5),
    (4, 'unity_consciousness', 'Unity Consciousness', NULL, 'The Transcendence of Prakriti', 'Unity consciousness is described as the consciousness of the Guru—the rarest and most difficult attainment. It comes only when one has transcended prakriti, the entire domain of natural forces. The process of attaining it proceeds through flashes of experiential awareness: what you are experiencing, you cannot really explain. Even if you try, you will be able to explain only a drop of it. But because of this experience, it will remain in your awareness, and you will never be prepared to lose it.

The lived experience at this level is characterized by a paradox. On one hand, there is a total absence of attraction for anything in the world of chit (consciousness as normally experienced). Only a survival compulsion keeps the person functional. This is the stage when the paramount importance is for survival—somehow the yogi must maintain the body. On the other hand, there is an attraction to something so immeasurably higher that the impulse to withdraw from the world is not repulsive (as it might be for someone merely disgusted with life) but magnetic—the pull of a force that the person cannot fully comprehend.

The critical distinction between God-realized souls and those in Unity consciousness is their capacity for action in the world. Those who have attained merger in the God plane cannot willfully descend back to the waking, dreaming, or sleeping planes. They depend on Divine grace and counsel others to pray. But those who are in the Unity plane can directly descend to the waking plane and intervene. This is why the masters who operate from Unity consciousness are able to function in the material world with full effectiveness while simultaneously abiding in the highest spiritual reality.

The Gita’s description of the brahmī sthiti—the Supreme Divine State—refers to this level. When a person enters Unity and does not fall back, when they remain there and descend only out of their own sweet will, this is called Brahma nirvāṇa if attained after leaving the body, and jīvanmukta (liberated while living) if attained while still embodied.

•  •  •', 6),
    (4, 'cosmic_consciousness', 'Cosmic Consciousness', NULL, 'The Totality of Sat and Chit', 'Cosmic consciousness, described as the Purushottama consciousness or the Krishna consciousness, represents the totality of chit and sat—the Supreme Being fully manifest. The person established in cosmic consciousness possesses an extraordinary quality: they feel hunger like a hungry person, they experience the material world fully, yet their consciousness is never diluted by any condition. Food or no food, comfort or discomfort, honor or dishonor—the consciousness remains whole, undimmed, and fully operative on every plane simultaneously.

Sri Aurobindo’s evolutionary framework illuminates this state from a different angle. He envisions it not merely as an individual attainment but as the next stage of evolution for consciousness itself. Just as life developed out of matter, and mind out of life, a still higher form of consciousness—what he calls the supramental Truth-Consciousness—is destined to develop out of the mind. This highest consciousness knows the universe from inside, as the Divine knows it. If there is any limitation of knowledge or power at this level, it is a willed and conscious diminution for the sake of the harmony and development of the whole.

The lived experience of cosmic consciousness, as described across these traditions, is one in which every apparent contradiction is resolved—not intellectually but existentially. The person is simultaneously fully in the world and fully beyond it, fully individual and fully universal, fully active and fully still. This is not a paradox to be understood but a reality to be inhabited.', 7);

-- -----------------------------------------------------------------------------
-- D5 — Five Sheaths  (5 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (5, 'annamaya_kosa', 'Annamaya Kośa', NULL, 'The Sheath of Matter', 'Annamaya literally means “made of food.” This outermost sheath is the physical body—the structure of skin, bone, muscle, organ, and tissue that is born from matter, sustained by matter, and dissolves back into matter at death. It is composed of the five gross elements (pañca mahābhūtas) and linked to the root chakra and the earth element. Its dominant guṇa is tamas—inertia, density, and unconsciousness. Its characteristic shakti is āvaraṇa shakti, the power of concealment, which veils the subtler dimensions of being behind the dense screen of physicality.

A person who resides predominantly at the level of annamaya kośa believes that they are only the physical body. Their identity is fused with the material form. They are attached and consumed solely by the physical: the pleasures of the body, the comforts of matter, the satisfaction of sensory appetites. Such persons orient their lives around physical fitness, bodily appearance, food, dress, comfort, sports, and the tangible accumulation of material security. They are drawn to activities like bodybuilding, athletics, and aerobics—not as doorways to subtler awareness, but as ends in themselves.

The experiential quality of this dwelling is characterized by what the tradition calls inertia. There is a solidity and groundedness to this person’s existence, but also a heaviness, a density that resists the upward movement of consciousness. Their concerns are survival concerns: food, shelter, safety, physical pleasure, and physical pain. Their suffering is predominantly physical—illness, injury, deprivation, the anxiety of bodily vulnerability, and the terror of death, which for them is absolute annihilation since they have no experiential reference to anything beyond the body.

When annamaya kośa is out of balance—through poor diet, lack of movement, excess tamasic foods, or neglect of the body’s elemental needs—the consequences ripple outward into every other dimension. The physical body is the foundation. If the foundation is unstable, the entire edifice of subtle experience totters. This is why the tradition, even while pointing to the transcendence of the physical, never dismisses it. All modern medicine acts on this kośa, and the first practices prescribed by yoga—āsana, fasting (upavāsa), inner purification (tatvashudhi), and austerity (tapashcharyā)—are aimed precisely at refining this sheath.

“The personality or constitution of the individual—comprising physical, mental, social and emotional traits—all depend on the condition of annamaya kośa, the formation of which continues in each birth or life one has.”  — Koshas-Gunas', 1),
    (5, 'pranamaya_kosa', 'Prāṇamaya Kośa', NULL, 'The Sheath of Vital Energy', 'Moving inward from the body, we encounter the prāṇamaya kośa—the sheath of vital energy, the dimension of life-force (prāṇa) that animates the otherwise inert physical form. This sheath contains the five prāṇas—prāṇa (inward movement), apāna (downward excretion), udāna (upward expression), samāna (digestive assimilation), and vyāna (circulatory distribution)—the vital winds that govern breathing, digestion, circulation, elimination, and expression. Its dominant guṇa is rajas—activity, movement, dynamism. Its characteristic shakti is kriyā shakti, the power of action.

A person who dwells predominantly at the level of prāṇamaya kośa experiences themselves as a field of energy rather than merely a lump of matter. They have, at least temporarily, intuited that they are the finer force animating the physical form, not the form itself. Such people are characteristically very active and energetic. They are drawn to practices that cultivate and direct vital energy—prāṇāyāma, vigorous exercise, dynamic meditation, outdoor activity—and they give importance to both physical movement and the subtle currents of vitality that underlie it.

The experiential quality of this dwelling is characterized by movement, dynamism, and a heightened sensitivity to energetic states. This person notices when their energy is high or depleted, when a room feels charged or stagnant, when certain foods enliven them and others drag them down. Their suffering arises not from physical pain alone but from energetic disturbance—fatigue, restlessness, the scattered quality of unregulated prāṇa, the feeling of being “wired but tired,” the anxiety that comes when the vital winds blow chaotically rather than rhythmically.

The prāṇamaya kośa serves as the critical bridge between body and mind. It interconnects the annamaya kośa with the manomaya, vijñānamaya, and ānandamaya sheaths. It transmits the intentions of the mental and emotional sheaths into physical action through alterations in the breath—which is why the breath changes when we are afraid, aroused, concentrated, or at peace. This is not metaphor; it is mechanism. The tradition understands that the rhythms of the breath are intimately tied to the earliest and most fundamental layers of mental life.

When prāṇamaya kośa is imbalanced, the person experiences a characteristic set of disturbances: irregular breathing, digestive irregularity, circulatory problems, chronic fatigue alternating with manic energy, and a pervasive sense that their “battery is low” or erratically charged. The polyvagal lens described by Stephen Porges maps onto this dimension with striking precision: the dorsal vagal immobilization response corresponds to tamasic prāṇic collapse, the sympathetic fight-flight response to rajasic prāṇic agitation, and the ventral vagal social engagement response to sattvic prāṇic equilibrium.', 2),
    (5, 'manomaya_kosa', 'Manomaya Kośa', NULL, 'The Sheath of Mind', 'The manomaya kośa is the mental sheath—the dimension of thoughts, emotions, desires, memories, and imagination. It contains both the jñānendriyas (organs of perception—hearing, touch, sight, taste, smell) and the karmendriyas (organs of action—speech, hands, legs, reproduction, excretion). It is nourished by knowledge and education. Its guṇa composition is a mixture of sattva and tamas—it possesses both the capacity for knowing and the tendency toward veiling. Its characteristic shakti is icchā shakti, the power of will and desire.

The person who resides predominantly at the level of manomaya kośa lives in a world of feelings, desires, impressions, and emotional reactions. Their identity is woven from thoughts and desires that identify with form, name, position, and qualities. They are emotional by nature. This person may possess keen aesthetic sensitivity—a fine appreciation for music, dance, drama, visual art, and the emotional textures of human experience—but they lack the cognitive discriminative capacity of the next sheath. They feel intensely but cannot always discern why they feel what they feel, or whether what they feel is leading them toward truth or illusion.

The lived quality of this dwelling is characterized by fluctuation. The mind, in the Vedantic view, is inherently vikari—changeful, restless, oscillating between saṅkalpas (constructive intentions) and vikalpas (aversive rejections). The person at manomaya experiences life as an emotional rollercoaster: joy alternating with sorrow, attraction with repulsion, confidence with self-doubt, love with fear. Their vrittis (mental modifications)—lust, anger, greed, attachment, pride, jealousy—are in continual fluctuation. This is the sheath where most of humanity dwells for most of their lives, caught in the weather systems of the mind.

The suffering that arises from dwelling at this layer is psychological suffering in its most recognizable forms: anxiety, depression, obsession, emotional reactivity, the anguish of unfulfilled desires, the bitterness of perceived injustice, the loneliness of feeling misunderstood. Because manomaya kośa processes experience through the lens of preference and aversion, everything that happens is immediately sorted into “for me” or “against me,” “pleasant” or “unpleasant,” “wanted” or “unwanted.” This binary sorting mechanism is extraordinarily useful for navigating the sensory world, but it is also the engine of suffering, because it can never rest. There is always something to want and something to fear.

The tradition prescribes specific practices for refining this sheath: meditation, alternate nostril breathing (nāḍī shodhana), the yamas and niyamas (ethical observances), and selfless service (karmayoga). These practices do not suppress the mind but gradually teach it to observe itself, to notice the arising of a thought or emotion without being swept away by it, to create a sliver of space between stimulus and response in which choice becomes possible.', 3),
    (5, 'vijnanamaya_kosa', 'Vijñānamaya Kośa', NULL, 'The Sheath of Discernment', 'Vijñāna literally means intellect or discerning wisdom. This fourth sheath is the dimension of buddhi—the discriminative faculty that lies beneath the processing, reactive mind. It is composed of the intellect combined with the five sensory organs, but its function is qualitatively different from the mind’s function. Where manas (mind) receives, reacts, and processes, buddhi evaluates, discriminates, and decides. Where manas says “I want,” buddhi asks “Is this truly good for me?” Where manas is caught in the immediacy of experience, buddhi can step back and see the larger pattern, the longer arc, the deeper truth.

Its dominant guṇa composition is sattva mixed with rajas—clarity energized by purposeful activity. Its characteristic shakti is jñāna shakti, the power of wisdom. It is related to the throat chakra and the air element, and it is precisely this sheath that distinguishes human beings from animals. Animals possess annamaya, prāṇamaya, and manomaya—bodies, energy, emotions, and basic mental processing—but they lack buddhi, the capacity for self-reflective discrimination between what is good and bad, right and wrong, eternal and illusory.

The person who resides predominantly at the level of vijñānamaya kośa is knowledgeable and wise. They love literature, creative expression, and intellectual inquiry. They are good orators, clear thinkers, and natural leaders. This fourth sheath is the wisdom that lies beneath the processing, thinking aspect of the mind. This person knows, decides, judges, and discriminates between the information they process. They are innovative. Discovery, research, and management are the domains where these people naturally gravitate.

The experiential quality of this dwelling is characterized by clarity, purposefulness, and the capacity for what we might call moral and intellectual vision. The person at vijñānamaya does not merely react to life; they understand it. They can see through the surface turbulence of emotional experience to the structural patterns beneath. They make decisions not from impulse or emotional pressure but from a considered assessment of what is true, what is valuable, and what will genuinely serve the larger good. Their inner life is characterized not by the rollercoaster of manomaya but by a steadier flame—still subject to flickering, but fundamentally oriented toward light.

The suffering that arises at this layer is subtler but no less real: the suffering of excessive analysis, of intellectual pride, of ego-identification with one’s intelligence and judgment. Because vijñānamaya is nourished by ego (ahaṃkāra) as well as by wisdom, there is a danger of confusing one’s capacity for discernment with omniscience—of mistaking the map for the territory, the model for reality. The person who dwells exclusively at this level may become overly cerebral, disconnected from the emotional and physical dimensions of life, trapped in a crystalline palace of ideas that is brilliant but cold.

The tradition addresses this by prescribing the study of scriptures (svādhyāya), right inquiry (“Who am I?”), and deep meditation—practices that turn the discriminating intellect upon itself, revealing that even the most refined thought is still a modification of consciousness, still a sheath, still a covering over something more essential. Vijñānamaya kośa is the doorway to transcendence, but it is not itself the destination.', 4),
    (5, 'anandamaya_kosa', 'Ānandamaya Kośa', NULL, 'The Sheath of Bliss', 'Ānanda means bliss—not pleasure, not happiness in the ordinary sense, but the unconditioned, objectless joy that is the fundamental stuff of existence itself. The ānandamaya kośa is the innermost sheath, the most subtle veil covering the Ātman (the Self). It resides in the causal body (kāraṇa sharīra) and contains the vāsanās—the latent impressions and seed tendencies that are the causative blueprint for all the outer sheaths. It is the storehouse of all our impressions and latent energies; when these hidden impressions express themselves as feelings and thoughts, they take the form of the subtle body, and the same material works out as perceptions and actions in the gross body.

Its characteristic shakti is bhoga shakti—the power of pure experience, joy, and pleasure in the deepest sense. We glimpse this kośa every night in dreamless sleep, when the agitation of the mind and the striving of the intellect are temporarily suspended and consciousness rests in itself. Upon waking, we say “I slept well”—that sense of refreshment, that residual feeling of having been immersed in something restful and whole, is the afterglow of contact with the ānandamaya kośa.

Persons experiencing ānandamaya kośa are stable in behavior and firm in decision-making. They are happy in every state of life. They appreciate a higher order of things and thinking—nature, prayer, meditation, connection with the divine—not as occasional refuges from the stress of life but as the very ground of their being. They are self-realized persons. Their equanimity is not the forced calm of someone suppressing emotion but the natural ease of someone who has found, through direct experience, that their essential nature is already whole, already at peace, already sufficient.

The experiential quality of this dwelling is characterized by what the tradition calls intuition and idea-generation—not the discursive reasoning of buddhi, but a direct, unmediated knowing that arises from the depths of being. This person does not figure things out; things reveal themselves. Their creativity is not effortful but effortless, arising from a place of fullness rather than lack. Their relationships are characterized by unconditional warmth—not because they have worked hard to be loving, but because love is what naturally flows when the barriers of ego, fear, and self-protection are thinned to near-transparency.

Even at this refined level, the tradition is careful to note that the ānandamaya kośa is still a sheath—still a covering, however gossamer, over the Ātman. The bliss experienced here, while incomparably more refined than any sensory or emotional pleasure, is still conditioned, still a modification of consciousness, still material in the Vedantic sense. The ultimate aim of the pañca kośa viveka—the discriminative analysis of the five sheaths—is to recognize that even this bliss is not the final reality, that the Self is beyond all five sheaths, beyond all three bodies, beyond all states of consciousness.

“A person remains always happy and has a cheerful personality if he attains the Ānandamaya Kośa, a state of eternal peace, love and harmony. This transformation makes us videha—free from the body, detached from the body.”  — Pancha-Kosha Theory of Personality

•  •  •', 5);

-- -----------------------------------------------------------------------------
-- D6 — Subtle Energies  (5 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (6, 'earth', 'Earth', NULL, 'The Ground of Stability', 'Earth is the densest and most manifest of the five elements. It gives form, shape, and structure to the physical body. In the body, Pṛthivī manifests as bone, muscle, skin, nāḍī (tissue fibers), and hair. Its tanmātra is Gandha (smell), and its sense organ is the nose. Its fundamental quality is Kharatwa—roughness, solidity, and stability. The bija mantra associated with Earth is ‘Lam,’ and it is seated in the Mūlādhāra Chakra at the base of the spine.', 1),
    (6, 'water', 'Water', NULL, 'The Flow of Feeling', 'Water is the element of fluidity, cohesion, and binding. In the body, Jala manifests as semen, reproductive fluids, fat, urine, and saliva. Its tanmātra is Rasa (taste), and its sense organ is the tongue. Water’s qualities include adhesion, cooling, and liquidity. Its bija mantra is ‘Vam,’ and it is seated in the Svādhiṣṭhāna Chakra, associated with joy and well-being.', 2),
    (6, 'fire', 'Fire', NULL, 'The Flame of Transformation', 'Fire is the element of transformation, penetration, and illumination. In the body, Agni manifests as hunger, thirst, sleep, light perception, and drowsiness. Its tanmātra is Rūpa (form or vision), and its sense organ is the eye. Fire governs digestion, metabolism, and the conversion of experience into understanding. Its bija mantra is ‘Ram,’ and it is seated in the Maṇipūra Chakra, associated with wisdom and personal power. Indian culture personifies fire as Agni Deva, depicted with two faces—symbolic of fire as both life-giver and life-taker.', 3),
    (6, 'air', 'Air', NULL, 'The Breath of Movement', 'Air is the element of motion, force, and kinetic energy. It represents all forces and the movement that transpires as their result. In the body, Vāyu manifests as the movements of walking, breathing, the motor and sensory nerve impulses, the peristaltic motion of the gut, and all muscular contraction and expansion. Its tanmātra is Sparsha (touch), and its sense organ is the skin; its organ of action is the hand. Air’s bija mantra is ‘Yam,’ and it is seated in the Anāhata Chakra, associated with compassion.', 4),
    (6, 'space', 'Space', NULL, 'The Container of Possibility', 'Space is the subtlest and most pervasive of the five elements. It is not empty space but Ether—a subtle dimension of existence, the container within which all other elements operate. In the body, Ākāśa is present in the voids—the nostrils, mouth, abdomen, and all channels and pores. Its tanmātra is Shabda (sound), and its sense organ is the ear. Its chief quality is non-resistance (Apratighatatwa), and it is associated with expansion and vibration. Its bija mantra is ‘Ham,’ and it governs the Vishuddhi (Throat), Ājñā (Third Eye), and Sahasrāra (Crown) Chakras.

The Brahmavidya tradition enumerates the fivefold Ākāśa in the human being as: desire to possess, desire to repel, shame, fear, and forgetfulness. These are the psychological spaciousnesses—or their distortions—that arise from the Space element.', 5);

-- D6 pole descriptions (15 rows)
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'A person in whom the Earth element is well-proportioned experiences groundedness, physical stability, and a secure sense of belonging. There is structural integrity in the body—strong bones, healthy teeth, firm musculature, and resilient skin. Psychologically, such a person feels rooted, patient, and reliable. They relate well to the material world without being consumed by it. There is a quality of steadiness in their personality, and they can weather emotional storms without losing their foundation.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 6 AND c.slug = 'earth';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Pṛthivī becomes disproportionate through excess, heaviness and stagnation pervade the system. Physically, this may manifest as obesity, lethargy, congestion, and sluggish digestion. The joints may stiffen, and the body feels dense and immovable. Emotionally, excessive Earth produces attachment, possessiveness, resistance to change, and a kind of mental inertia that makes it difficult to entertain new ideas or release old patterns. The person becomes ‘stuck,’ clinging to familiar routines, relationships, and beliefs well past their usefulness. Cognitively, there is dullness—a fog that settles over the mind, making clear thinking effortful.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 6 AND c.slug = 'earth';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the Earth element is depleted, the person loses their grounding. Physically, this may appear as low bone density, weakness in the legs and feet, poor structural support, and a general sense of being ‘unanchored.’ Emotionally, there is insecurity, anxiety, a feeling of not belonging, and difficulty trusting others or the world. The Mūlādhāra Chakra, when underactive, produces fearfulness, nervousness, and a persistent sense of unwelcome. The person may constantly seek external validation because they lack an internal foundation.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 6 AND c.slug = 'earth';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Balanced Water gives a person emotional fluidity—the capacity to feel deeply without being overwhelmed, to adapt to changing circumstances with grace, and to maintain healthy intimacy and creative expression. The body’s fluids circulate properly: digestion works smoothly, reproductive health is sound, and the skin has a healthy luster. The person experiences joy, sensuality, and creative vitality without excessive attachment.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 6 AND c.slug = 'water';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'An excess of Water creates emotional flooding. The person becomes hypersensitive, prone to sentimentality, and may be easily overwhelmed by feelings. Physically, excess Water manifests as edema, mucus congestion, heaviness in the lower abdomen, and sluggish lymphatic function. The Svādhiṣṭhāna Chakra in overactive states produces excessive emotionality, sexual preoccupation, and a clinging quality in relationships.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 6 AND c.slug = 'water';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Water is depleted, dryness and rigidity enter the system. Physically, the skin becomes dry, the joints creak, the mouth feels parched, and the eliminative functions become strained. Emotionally, the person becomes cold, distant, and unable to access or express feelings. There is a quality of emotional barrenness—an inability to connect with others at the level of intimacy or vulnerability. The Svādhiṣṭhāna Chakra becomes underactive, producing impassivity and emotional withdrawal.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 6 AND c.slug = 'water';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Balanced Fire produces strong digestion, clear vision (both physical and intellectual), sharp discrimination, and the capacity for decisive action. The person has healthy self-esteem, courage, and a natural authority that comes from inner clarity rather than domination. There is warmth in their personality—an ability to illuminate situations and inspire others. Metabolic processes function optimally, and the person can transform both food and experience into nourishment and wisdom.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 6 AND c.slug = 'fire';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Excess Fire creates burning—both literal and figurative. Physically, this appears as inflammation, hyperacidity, skin rashes, fever, and excessive heat. The Pītta doṣa, which is dominated by Fire, when aggravated leads to Tīkṣṇa Agni—a digestive fire so intense that it begins to consume the body’s own tissues. Emotionally, excessive Fire produces irritability, anger, impatience, competitiveness, and the need to dominate or control. The Maṇipūra Chakra in overactive states generates imperious and aggressive behavior, and the person may become consumed by ambition at the expense of relationships and inner peace.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 6 AND c.slug = 'fire';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Fire is weak, the digestive capacity falters. Physically, this leads to poor metabolism, loss of appetite, and accumulation of toxins (Manda Agni, where Kapha dominates, producing sluggish digestion and frequent indigestion). Emotionally, deficient Fire results in low self-esteem, confusion, and reluctance—a lack of the inner flame needed to take initiative or make clear decisions. The person may feel directionless, constantly deferring to others, and unable to assert their needs or values.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 6 AND c.slug = 'fire';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Balanced Air gives freedom and lightness. The person moves through life with grace, adaptability, and openness. The nervous system functions smoothly, the breath is deep and steady, and the capacity for love and compassion flows naturally. The Anāhata Chakra, when balanced, produces a great capacity for love without attachment—a warmth that extends to all beings without grasping. When the air element is balanced, one can freely give and receive love, feel light and open, feel motivated and innovative, and express mental agility.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 6 AND c.slug = 'air';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Excess Air produces scattering, instability, and anxiety. This is the Vāta imbalance—the most frequently discussed doṣic disturbance in Āyurveda, because Vāta (Air-Ether) governs all movement, and its derangement affects every other system. Physically, excessive Air causes dryness, tremors, joint pain, constipation (paradoxically through irregular motility), irregular heartbeat, and difficulty sleeping. Emotionally, the person becomes anxious, fearful, scattered, and unable to concentrate. The mind races from thought to thought without landing. There is a quality of ungroundedness—as though the person has been uprooted and is being blown about by forces they cannot control. The Anāhata Chakra, when overactive, can produce an excessive, suffocating love that borders on obsession.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 6 AND c.slug = 'air';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Air is depleted, there is stagnation of movement. The person feels stuck, unable to change or adapt. Circulation diminishes, nerve impulses slow, and creativity stalls. The breath becomes shallow and mechanical. Emotionally, deficient Air produces coldness, an inability to connect with others, and a rigidity that prevents the heart from opening. When the Anāhata Chakra is underactive, the person tends to be cold and unfriendly, unable to access the warmth of genuine human connection.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 6 AND c.slug = 'air';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Balanced Space provides the inner room needed for all other elements to function. It manifests as trust, creativity, clear communication, and the capacity for higher perception. The person feels expansive without being ungrounded, open without being diffuse. The Vishuddhi Chakra allows free and truthful expression; the Ājñā Chakra supports intuition and insight; and the Sahasrāra Chakra enables connection with the transcendent. Balancing the Space element can give one the highest self-healing powers.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 6 AND c.slug = 'space';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Excess Space creates a sense of emptiness, dissociation, and disconnection. The person feels uncontained—as though their boundaries have dissolved and they cannot distinguish between themselves and the world. This may manifest as depersonalization, spaciness, and an inability to focus or commit. The Vishuddhi Chakra in overactive states produces excessive talkativeness and poor listening. The Ājñā Chakra, when overstimulated, produces a tendency to live in imagination and fantasy, and in extreme cases may manifest as hallucinations or persistent daydreaming. The Crown Chakra, when overactive, may cause the person to neglect basic physical needs in pursuit of spiritual abstraction.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 6 AND c.slug = 'space';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Space is depleted, there is claustrophobia of the soul. The person feels constricted, unable to express themselves, and cut off from higher awareness. The Vishuddhi Chakra becomes blocked, producing shyness, dishonesty, and an inability to voice one’s truth. The Ājñā Chakra, when underactive, produces a tendency to rely on others for direction, confusion, and susceptibility to superstition. The person lacks the inner spaciousness required for insight, creativity, or spiritual connection.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 6 AND c.slug = 'space';

-- -----------------------------------------------------------------------------
-- D7 — Phenomenological Dimensions  (8 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (7, 'valence', 'Valence', NULL, 'Sukha–Duḥkha Tone of Experience', 'Valence is the first vibration of experience—the immediate yes or no that arises before thought, before story, before morality. In Vedic terms, it is the raw movement of rāga (pull) and dveṣa (push), the subtle evaluator that precedes cognition and quietly governs karma.

Below, valence is explored across three states of being, followed by two contrasting vignettes situated in a single modern scenario.

I. The Three States of Valence', 1),
    (7, 'arousal', 'Arousal', NULL, 'Intensity / Activation', 'Prāṇic amplitude of lived experience

Arousal is the volume knob of consciousness. It determines how forcefully experience arrives, how urgently it demands response, and how compressed or dilated the moment feels. In Vedic terms, it is the movement of prāṇa under the influence of rajas (over-activation) and tamas (under-activation), with sattva as regulated flow.

Arousal does not decide what is felt—that is valence.It decides how intensely life presses upon the system.

I. The Three States of Being', 2),
    (7, 'clarity', 'Clarity', NULL, NULL, 'Phenomenal resolution of lived experience

Clarity is the definition of experience—how sharply reality presents itself to awareness. It is not truth, intelligence, or correctness; it is resolution. In Vedic terms, clarity is the functioning of buddhi when unobscured by tamas (fog) or rajas (over-noise). It determines whether experience feels knowable or confusing, inhabited or dreamlike.

Clarity answers a quiet but decisive question:

Can I see what is actually happening—internally and externally—without distortion?

I. The Three States of Being', 3),
    (7, 'self_location', 'Self-Location', NULL, 'Spatiality', 'Where “I” am experienced to be

Self-location is the felt seat of the self. It answers a deceptively simple question:

From where am I experiencing this moment?

Ordinarily, the self feels located inside the body—behind the eyes, in the chest, or at the center of action. Yet this location is phenomenological, not anatomical. In Vedic terms, it reflects whether awareness is rooted in the body-mind (deha-abhiniveśa), displaced into observation, or diffused across space.

Self-location determines whether life feels inhabited or watched, immediate or remote.

I. The Three States of Being', 4),
    (7, 'temporal_orientation', 'Temporal Orientation', NULL, 'Subjective Time', 'Where awareness is seated in the flow of time

Temporal orientation is not clock time. It is the felt posture of consciousness toward time—whether awareness leans backward into memory, forward into anticipation, or rests in the immediacy of now. In Vedic terms, it reflects one’s relationship to kāla: whether time is a teacher, a threat, or a field of presence.

Temporal orientation determines whether life feels burdened, rushed, or alive.

I. The Three States of Being', 5),
    (7, 'agency', 'Agency', NULL, 'Ownership of Action', 'The felt authorship of thought, choice, and behavior

Agency is not objective control. It is the experience of authorship—the sense that “I am initiating this,” rather than being driven by impulse, compulsion, or external force. In Vedic psychology, distorted agency emerges from confusion between ahaṅkāra (egoic doership) and the deeper witnessing presence. Healthy agency neither collapses into helplessness nor inflates into control—it functions with responsibility and surrender.

Agency determines whether life feels participatory or imposed.

I. The Three States of Being', 6),
    (7, 'relational_quality', 'Relational Quality', NULL, 'Intersubjectivity / Context', 'The felt field of “with-ness”

Relational quality is not just interaction; it is the background atmosphere of belonging or alienation in which experience unfolds. In Vedic terms, it reflects whether one’s participation in the lokasaṃgraha—the shared fabric of life—is attuned or distorted. Even solitude has relational quality: one can be alone with the world or isolated from it.

Relational quality determines whether life feels inhabited together or endured alone.

I. The Three States of Being', 7),
    (7, 'somatic_presence', 'Somatic Presence', NULL, 'Embodiment', 'The degree to which life is felt from the inside

Somatic presence is the inhabitation of experience through the body. It determines whether perception, emotion, and thought are anchored in flesh and breath—or float abstractly above them. In Vedic terms, embodiment reflects the integrity of the annamaya and prāṇamaya kośas as living gateways of awareness, rather than inert shells.

Somatic presence determines whether life is felt, regulated, and metabolized—or merely conceptualized.

I. The Three States of Being', 8);

-- D7 pole descriptions (24 rows)
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Pleasant and unpleasant are both allowed to appear without commandeering the self.

Internal Landscape

Somatic Base (Physical)The body feels responsive rather than reactive. Pleasant sensations are enjoyed without tightening; unpleasant sensations are registered without collapse. There is a gentle elasticity in the gut and chest—no bracing, no chasing.

Emotional Current (Vital)Pleasure does not demand repetition. Discomfort does not demand escape. The emotional field is fluid, with no dominant hunger. There is an underlying tone of trust—that experience can be met as it comes.

Cognitive Map (Mental)Thought does not immediately label sensations as “good for me” or “bad for me.” The mind stays descriptive rather than evaluative. Meaning is allowed to emerge rather than being imposed.

Inner Presence (Psychic)At the soul level, there is samatva—equanimity. Sukha and duḥkha are known as movements within prakṛti, not verdicts on the self. Valence is seen, not obeyed.

External Conduct

Decisions are made without urgency. Work is engaged sincerely but without emotional overinvestment. Relationships have space—affection without clinging, disagreement without aversion. Habits feel clean because they are not compensatory.

Day-in-the-Life Vignette (Equilibrium)

He receives a message: a project proposal has been rejected. A brief contraction in the chest, a dull unpleasantness. He notices it while standing at the sink. He exhales, lets the shoulders drop. The unpleasant tone does not become a story about failure. Ten minutes later, he drafts a revised plan. In the evening, he enjoys dinner without replaying the email. The day remains whole.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 7 AND c.slug = 'valence';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Experience is hijacked by attraction or aversion.

Internal Landscape

Somatic Base (Physical)The body is pulled forward or recoils. In craving, there is a leaning tension—jaw tight, breath shallow. In aversion, there is bracing—gut clenched, shoulders raised. Sensation feels urgent.

Emotional Current (Vital)Pleasure carries desperation; discomfort carries threat. There is a constant undertone of “this must continue” or “this must stop.” Emotional neutrality feels intolerable.

Cognitive Map (Mental)The mind rationalizes: “I need this to feel okay” or “I can’t handle this.” Experience is misinterpreted as a command. Valence masquerades as truth.

Inner Presence (Psychic)The witnessing self collapses into the wave. The soul forgets its seat and identifies with sensation. Rāga or dveṣa becomes destiny.

External Conduct

Work becomes compulsive or avoidant. Relationships become transactional—people are valued for how they regulate one’s internal tone. Habits harden into addictions, distractions, or rigid control patterns.

Day-in-the-Life Vignette (Excess)

She wakes already scanning for something pleasant—her phone, a message, a hit of reassurance. When none arrives, irritation blooms. At work, mild feedback feels like an attack. She replays it all day. In the evening, she binge-watches, eats past fullness, scrolls long after exhaustion. Pleasure is pursued frantically, yet relief never arrives.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 7 AND c.slug = 'valence';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Pleasant and unpleasant lose their signal value.

Internal Landscape

Somatic Base (Physical)The body feels dull or distant. Sensations are muted, as if filtered through cotton. There is little warmth, little sharpness.

Emotional Current (Vital)Neither desire nor aversion moves strongly. Life feels gray—not painful enough to flee, not pleasant enough to approach. Motivation is minimal.

Cognitive Map (Mental)Thoughts circle around “What’s the point?” Meaning feels inaccessible. Even positive events fail to register as rewarding.

Inner Presence (Psychic)The soul’s signal is faint. Not lost—but veiled. The lesson here is not restraint but re-contact.

External Conduct

Work is done mechanically. Relationships feel distant, not hostile. Habits drift toward inertia. Life continues, but without intimacy.

Day-in-the-Life Vignette (Deficiency)

He completes his tasks efficiently but without satisfaction. Compliments land flat. Criticism barely stings. In the evening, he sits quietly, unsure what he wants to do. Nothing feels wrong, but nothing feels alive.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 7 AND c.slug = 'valence';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Energy is available without agitation; rest is possible without collapse.

Internal Landscape

Somatic Base (Physical)The body feels alert but not tight. Breath is full and rhythmic. Muscles are engaged only as needed. There is readiness without bracing.

Emotional Current (Vital)Emotion has momentum but not urgency. Interest arises without compulsion. Calm is not dullness; excitement is not frenzy. There is a steady inner hum.

Cognitive Map (Mental)Thoughts appear at an appropriate pace. The mind can hold complexity without racing or freezing. Attention moves voluntarily rather than being yanked.

Inner Presence (Psychic)At the soul level, there is sthira–sukham—steadiness with ease. Prāṇa serves awareness rather than hijacking it. One feels capable.

External Conduct

Work unfolds in focused blocks. Breaks are taken before depletion. Relationships feel responsive rather than reactive. Habits support rhythm—sleep, food, movement align naturally.

Day-in-the-Life Vignette (Equilibrium)

She begins the morning with a clear sense of the day’s demands. During a challenging meeting, her heart rate rises slightly, sharpening attention. When it ends, the activation settles on its own. By evening, energy tapers gently. She sleeps without replaying the day. Nothing feels forced; nothing feels avoided.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 7 AND c.slug = 'arousal';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Energy exceeds the system’s capacity to metabolize it.

Internal Landscape

Somatic Base (Physical)The body is tight, keyed up. Breath is shallow or rapid. Jaw clenched, shoulders lifted. There is a sense of always being “on.”

Emotional Current (Vital)Urgency dominates. Even neutral situations feel charged. There is impatience with slowness, silence, or uncertainty. Rest feels unsafe.

Cognitive Map (Mental)Thoughts race, fragment, or catastrophize. The mind jumps ahead, scanning for threat or opportunity. Stillness is interpreted as danger or waste.

Inner Presence (Psychic)The witnessing self is drowned out by momentum. Prāṇa runs the show. The soul experiences itself as chased by time.

External Conduct

Work becomes frantic or perfectionistic. Multitasking replaces presence. Relationships suffer from irritability or emotional flooding. Habits skew toward stimulants, overwork, or constant distraction.

Day-in-the-Life Vignette (Excess)

He wakes already late, heart pounding before his feet touch the floor. Emails pile up faster than he can answer them. A minor delay spikes irritation. Even in the evening, his body won’t downshift—scrolling, snacking, pacing. Exhausted but wired, he collapses into shallow sleep.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 7 AND c.slug = 'arousal';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Energy falls below what engagement requires.

Internal Landscape

Somatic Base (Physical)The body feels heavy, slow, or inert. Breath is shallow but sluggish. Limbs feel weighted. Initiation requires effort.

Emotional Current (Vital)Emotion is muted. There is little urgency—but also little interest. Desire feels distant; aversion feels blunted. The dominant tone is fatigue.

Cognitive Map (Mental)Thoughts move slowly or loop repetitively. Concentration is difficult. Tasks feel overwhelming not because they are intense, but because energy is insufficient.

Inner Presence (Psychic)The soul feels veiled, not absent. Awareness remains, but prāṇa does not rise to meet life. The lesson here is re-ignition, not restraint.

External Conduct

Work is postponed or done mechanically. Social contact feels draining. Habits drift toward passivity—sleeping too much, scrolling without engagement, avoiding challenge.

Day-in-the-Life Vignette (Deficiency)

She sits at her desk staring at the screen. The task isn’t hard, but starting feels impossible. Hours pass without momentum. Even pleasant invitations feel like burdens. At night, she goes to bed early—not from satisfaction, but from depletion.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 7 AND c.slug = 'arousal';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Experience appears defined, navigable, and trustworthy.

Internal Landscape

Somatic Base (Physical)The body feels awake and oriented. Sensations have edges—pressure, warmth, movement are distinguishable. There is no buzzing or dullness. Breath supports alertness without strain.

Emotional Current (Vital)Emotions are recognizable as specific tones rather than vague moods. Sadness is sadness, not confusion. Interest is interest, not agitation. Feelings inform rather than flood.

Cognitive Map (Mental)Thoughts arise in coherent sequences. Attention can rest on one object without drifting or fragmenting. Decisions feel grounded because the relevant variables are visible.

Inner Presence (Psychic)At the soul level, there is viveka—discernment. Awareness trusts itself. The self feels located, not scattered. Even uncertainty is clear as uncertainty.

External Conduct

Work is structured and adaptive. Tasks are prioritized without obsession. Communication is precise, not over-explained. Habits are intentional because perception is reliable.

Day-in-the-Life Vignette (Equilibrium)

She reviews her schedule and notices a tight overlap between two commitments. The recognition is immediate and calm. She adjusts one meeting, informs the other party, and proceeds. Throughout the day, she knows when she is tired, when she is focused, and when she needs a pause. Nothing feels mysterious or overwhelming—just present.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 7 AND c.slug = 'clarity';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Experience is sharp but rigid; detail overwhelms meaning.

Internal Landscape

Somatic Base (Physical)The body feels tense and over-held. Eyes strain. Breath is shallow, as if maintaining constant alertness. There is little softness.

Emotional Current (Vital)Emotion is tightly monitored. Small fluctuations feel significant. There is anxiety about missing something, misunderstanding something, or making the wrong move.

Cognitive Map (Mental)Thought becomes hyper-analytical. Details multiply. The mind dissects endlessly, losing the gestalt. Certainty hardens into control.

Inner Presence (Psychic)The witnessing self narrows into the analyzer. Buddhi becomes a blade without a sheath. Insight loses humility.

External Conduct

Work becomes perfectionistic. Decisions are delayed by over-analysis. Relationships suffer from excessive explanation or correction. Habits skew toward micromanagement and mental rigidity.

Day-in-the-Life Vignette (Excess)

He rereads an email for the fifth time, adjusting phrasing minutely. A colleague’s casual comment echoes for hours. At home, he replays conversations, searching for hidden meanings. Everything is clear—but nothing is at rest.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 7 AND c.slug = 'clarity';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Experience lacks definition; orientation is lost.

Internal Landscape

Somatic Base (Physical)The body feels dull or disconnected. Sensations blur together—fatigue, hunger, tension are hard to distinguish. There is a sense of floating or heaviness.

Emotional Current (Vital)Emotion is vague. One feels “off” without knowing why. Irritability or sadness emerges without a clear object.

Cognitive Map (Mental)Thoughts are scattered or slow. Decisions feel confusing. Attention slips easily. Reality can feel unreal or distant.

Inner Presence (Psychic)The soul’s signal is obscured. Not absent—just veiled. There is diminished trust in one’s own perception.

External Conduct

Work feels disorganized or overwhelming. Communication becomes imprecise. Habits drift—sleep, eating, and focus lose rhythm. Life feels slightly unreal.

Day-in-the-Life Vignette (Deficiency)

She opens her laptop but cannot decide where to begin. Tasks blur together. A mild sadness lingers without cause. By evening, she feels exhausted without having done much. The day passes like a dream she cannot fully recall.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 7 AND c.slug = 'clarity';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Awareness is stably seated within the body and situation.

Internal Landscape

Somatic Base (Physical)The body feels occupied from within. Sensations arise where they occur—feet feel the ground, hands feel contact. There is weight and balance. Posture supports presence.

Emotional Current (Vital)Emotions are contained rather than spilling outward or collapsing inward. Feeling arises here, in the body, not at a distance. There is an implicit sense of safety in occupying one’s own space.

Cognitive Map (Mental)Attention is oriented outward from a stable center. Perception flows from “here” to “there” without confusion. Thoughts reference the body as the anchor point.

Inner Presence (Psychic)At the soul level, there is sthiti—abidance. Awareness knows itself as present in the body but not limited to it. The witness is near, not aloof.

External Conduct

Movement is coordinated and intentional. Work feels participatory rather than observational. Relationships feel intimate without being intrusive. Habits support grounding—regular meals, movement, rest.

Day-in-the-Life Vignette (Equilibrium)

She walks into a crowded room and feels her feet first. The noise registers, but it does not displace her. During conversations, she feels herself speaking from her chest, listening from her body. When she leaves, she feels complete—nothing left behind.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 7 AND c.slug = 'self_location';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The self retreats from the body into distance or surveillance.

Internal Landscape

Somatic Base (Physical)The body feels faint, distant, or unreal. Sensations are muted or delayed. There is a sense of hovering above or behind the body.

Emotional Current (Vital)Emotion is flattened or abstracted. Feelings are analyzed rather than felt. Safety is sought through distance.

Cognitive Map (Mental)The mind narrates experience from the outside. Thoughts take the form: “I notice that I am…” rather than “I feel…” There is excessive self-monitoring.

Inner Presence (Psychic)The witness separates too far. Sākṣī becomes exile rather than refuge. Awareness floats without embodiment.

External Conduct

Work becomes observational rather than engaged. Social interactions feel performative. Habits skew toward over-thinking, avoidance of sensation, or excessive screen immersion.

Day-in-the-Life Vignette (Excess)

He attends a meeting but feels as though he is watching himself speak. His voice sounds distant, as if coming from someone else. Afterward, he cannot recall how he felt—only what he said. The day passes without landing.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 7 AND c.slug = 'self_location';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The self is pulled into objects, others, or sensations.

Internal Landscape

Somatic Base (Physical)The body feels invaded or porous. Sensations overwhelm boundaries. There is little sense of containment.

Emotional Current (Vital)Emotion spills outward. Others’ moods feel intrusive. Reactivity replaces presence.

Cognitive Map (Mental)Attention is pulled toward stimuli. Thoughts orbit external events. The sense of “where I am” depends on what is happening around.

Inner Presence (Psychic)The soul is diffused. Awareness is scattered across objects of experience rather than seated in itself.

External Conduct

Work becomes reactive. Boundaries in relationships blur. Habits are shaped by external pressures rather than internal rhythm.

Day-in-the-Life Vignette (Deficiency)

She enters the day already absorbed by messages, news, demands. Every interruption hijacks her. By evening, she feels exhausted, unsure where the day went—or where she went.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 7 AND c.slug = 'self_location';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Past, present, and future are available without domination.

Internal Landscape

Somatic Base (Physical)The body feels paced. Movements have rhythm rather than haste. Breath is steady, neither held nor hurried. There is a sense of arriving fully in each moment.

Emotional Current (Vital)Emotion flows without dragging residue from the past or projecting anxiety into the future. Feelings arise and complete themselves. The dominant tone is timeless sufficiency.

Cognitive Map (Mental)Memory informs without imprisoning. Planning occurs without obsession. Attention returns easily to what is happening now. Time feels like a river one is in, not a force pushing from behind or pulling ahead.

Inner Presence (Psychic)At the soul level, there is sthiti—abiding in the present while holding continuity. Awareness knows itself as untouched by time even as it moves within it.

External Conduct

Work unfolds sequentially. Tasks are finished before new ones are started. Relationships feel present rather than nostalgic or anticipatory. Habits align with natural cycles—work, rest, renewal.

Day-in-the-Life Vignette (Equilibrium)

She plans the week in the morning, then closes the calendar. During meetings, she listens fully rather than rehearsing the next task. When a memory arises in the afternoon, she notes it without being pulled back. The day ends with a sense of completion, not rush.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 7 AND c.slug = 'temporal_orientation';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Awareness is captured by memory or anticipation.

Internal Landscape

Somatic Base (Physical)The body feels tense or restless. There is forward-leaning posture in future-fixation, or heaviness and collapse in past-fixation. Breath mirrors this—either rushed or sighing.

Emotional Current (Vital)In future-dominance: anxiety, urgency, control-seeking.In past-dominance: regret, sadness, resentment.Emotion feels repetitive, as if replaying on a loop.

Cognitive Map (Mental)Thoughts orbit around what should have been or what might happen. The present moment feels thin, merely a bridge between mental time zones.

Inner Presence (Psychic)The soul is displaced from the now. Awareness identifies with narrative rather than presence. Kāla is experienced as enemy or judge.

External Conduct

Work becomes rushed or avoidant. Relationships are filtered through memory or expectation rather than direct encounter. Habits become compulsive—checking, rehearsing, revisiting.

Day-in-the-Life Vignette (Excess)

He wakes already thinking about a conversation from last night—or one yet to come. At work, he is physically present but mentally elsewhere. Even rest is haunted by anticipation. Time feels like it is always running out or already gone.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 7 AND c.slug = 'temporal_orientation';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The sense of time loses depth or direction.

Internal Landscape

Somatic Base (Physical)The body feels heavy or inert. Movement lacks momentum. Breath is shallow or monotonous. Days blur together.

Emotional Current (Vital)Emotion feels muted. There is little anticipation or recollection. Motivation wanes. Life feels stalled.

Cognitive Map (Mental)Planning feels pointless. Memory lacks emotional charge. The future feels vague or unreachable. Time becomes static.

Inner Presence (Psychic)The soul’s dynamism is veiled. Awareness remains, but without temporal texture. The lesson here is re-engagement, not urgency.

External Conduct

Work is done mechanically. Relationships drift without initiative. Habits lose rhythm—sleep, eating, activity blur.

Day-in-the-Life Vignette (Deficiency)

She looks at the clock, surprised it is already afternoon. The morning left no impression. The evening arrives without anticipation. Life feels like it is happening, but not progressing.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 7 AND c.slug = 'temporal_orientation';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Action flows with conscious participation but without egoic inflation.

Internal Landscape

Somatic Base (Physical)The body feels responsive rather than reactive. Movements begin from intention, not tension. Breath and posture support deliberate action.

Emotional Current (Vital)There is a sense of capability without urgency. Motivation arises steadily. Emotions accompany action but do not overpower it.

Cognitive Map (Mental)Thoughts form around “I can choose” rather than “I must” or “I can’t.” Decisions are weighed, then enacted. Responsibility feels dignified, not burdensome.

Inner Presence (Psychic)At the soul level, there is recognition: I participate in action, but I am not the total cause of all outcomes. This is karma yoga—engagement without egoic entanglement.

External Conduct

Work is proactive but not controlling. Relationships are accountable without domination. Habits are shaped intentionally rather than compulsively.

Day-in-the-Life Vignette (Equilibrium)

She receives critical feedback. She feels the sting but says, calmly, “Let me reflect and adjust.” She makes changes where needed, leaves what is irrelevant. She neither collapses nor defends reflexively. The action is hers, but not her identity.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 7 AND c.slug = 'agency';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The self assumes excessive responsibility for outcomes.

Internal Landscape

Somatic Base (Physical)The body is tense, forward-leaning. Jaw tight, breath shallow. There is a subtle gripping, as if holding the world together.

Emotional Current (Vital)Anxiety hides beneath competence. There is fear of failure and intolerance for uncertainty. Rest feels irresponsible.

Cognitive Map (Mental)Thoughts revolve around control: “If I don’t handle this, everything will collapse.” Responsibility becomes identity.

Inner Presence (Psychic)Ahaṅkāra expands. The self mistakes participation for omnipotence. Outcomes are personalized excessively.

External Conduct

Work becomes perfectionistic. Delegation is difficult. Relationships feel micromanaged. Burnout looms because one feels solely accountable for everything.

Day-in-the-Life Vignette (Excess)

He stays late correcting minor details no one asked him to fix. At home, he mentally replays tasks to ensure nothing was missed. Even praise feels incomplete—there is always more to secure.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 7 AND c.slug = 'agency';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The self feels acted upon rather than acting.

Internal Landscape

Somatic Base (Physical)The body feels heavy or slack. Movements are delayed. There is little initiative in posture or gesture.

Emotional Current (Vital)A tone of resignation or shame lingers. Motivation is low. Effort feels futile.

Cognitive Map (Mental)Thoughts repeat: “It doesn’t matter what I do.” Decisions are avoided. Responsibility feels overwhelming rather than empowering.

Inner Presence (Psychic)The witness is overshadowed by perceived powerlessness. The self confuses surrender with collapse.

External Conduct

Work is reactive. Opportunities are missed due to inaction. Relationships may lean toward dependency or avoidance. Habits drift without intention.

Day-in-the-Life Vignette (Deficiency)

She delays replying to an important email, convinced her response won’t matter. Tasks accumulate. When problems escalate, they confirm her belief of incapacity.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 7 AND c.slug = 'agency';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Connection without fusion; autonomy without isolation.

Internal Landscape

Somatic Base (Physical)The body feels open yet bounded. Breath flows easily during interaction. There is no bracing or collapsing when others enter the field.

Emotional Current (Vital)Emotion includes warmth and responsiveness. Empathy arises without overwhelm. One feels neither invisible nor overexposed.

Cognitive Map (Mental)Others are perceived as subjects, not threats or utilities. Interpretation is flexible. Misunderstandings are corrected rather than assumed.

Inner Presence (Psychic)At the soul level, there is saha-bhāva—a sense of shared being. Awareness recognizes itself in relation without losing itself.

External Conduct

Work involves collaboration without competition or withdrawal. Relationships include listening and speaking in balance. Habits support connection—regular contact, clear boundaries, restorative solitude.

Day-in-the-Life Vignette (Equilibrium)

She moves through the day meeting people’s eyes, responding appropriately, letting conversations end when complete. In the evening, she enjoys quiet without loneliness. Connection feels available, not compulsory.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 7 AND c.slug = 'relational_quality';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The self dissolves into others’ expectations and moods.

Internal Landscape

Somatic Base (Physical)The body feels porous. Tension arises quickly in social settings. There is little sense of boundary—others’ presence is felt as invasion.

Emotional Current (Vital)Emotion mirrors others excessively. Approval-seeking and fear of disconnection dominate. One’s own needs feel secondary or unclear.

Cognitive Map (Mental)Thoughts revolve around others’ reactions: “Did I upset them?” “Am I enough?” Meaning is outsourced to social feedback.

Inner Presence (Psychic)Awareness forgets its own center. Connection becomes survival strategy. The soul trades presence for acceptance.

External Conduct

Work becomes people-pleasing. Boundaries blur in relationships. Habits skew toward constant availability, over-communication, or emotional caretaking.

Day-in-the-Life Vignette (Excess)

He says yes automatically—to meetings, favors, emotional labor. By evening, he feels drained and resentful, unsure where his energy went. Connection has become depletion.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 7 AND c.slug = 'relational_quality';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The relational field thins or disappears.

Internal Landscape

Somatic Base (Physical)The body feels closed or withdrawn. Shoulders curl inward. Eye contact feels effortful or avoided.

Emotional Current (Vital)Emotion is muted or guarded. There is a low-grade loneliness or distrust. Connection feels risky or pointless.

Cognitive Map (Mental)Thoughts interpret others as distant, judgmental, or irrelevant. Meaning is constructed privately, without relational feedback.

Inner Presence (Psychic)The soul contracts into self-sufficiency. Awareness forgets its relational nature. Isolation masquerades as independence.

External Conduct

Work is done alone when possible. Relationships fade or remain superficial. Habits lean toward withdrawal—screens replace presence, routines replace dialogue.

Day-in-the-Life Vignette (Deficiency)

She passes through the day without real exchange. Messages go unanswered. Even when among people, she feels unseen. The world feels flat, like a backdrop rather than a shared space.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 7 AND c.slug = 'relational_quality';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Experience is fully lived through the body without overwhelm.

Internal Landscape

Somatic Base (Physical)The body feels warm, responsive, and inhabited. Breath moves naturally. Sensations—pressure, movement, temperature—are clear but not intrusive. There is a sense of being here.

Emotional Current (Vital)Emotion is felt in the body—tightness in the chest, warmth in the belly—without needing immediate discharge. Feelings rise, move, and settle. There is affect tolerance.

Cognitive Map (Mental)Thought references bodily signals. Decisions include gut sense alongside reasoning. The mind listens to the body rather than overriding it.

Inner Presence (Psychic)At the soul level, awareness recognizes the body as an ally and instrument, not an obstacle. Presence descends fully into form without losing spaciousness.

External Conduct

Work is paced with bodily feedback. Relationships include physical cues—posture, tone, proximity. Habits support embodiment: movement, rest, nourishment, breath.

Day-in-the-Life Vignette (Equilibrium)

She notices hunger before irritability sets in. She stretches when stiffness appears. During conversation, she senses when she needs to pause or speak. By evening, her body feels used, not depleted. Sleep arrives naturally.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 7 AND c.slug = 'somatic_presence';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The body dominates awareness.

Internal Landscape

Somatic Base (Physical)Sensations are loud and intrusive. Pain, tension, or pleasure hijack attention. The body feels overwhelming, demanding constant management.

Emotional Current (Vital)Emotion spills rapidly into sensation. Anxiety surges as tightness, anger as heat, sadness as heaviness. Regulation feels difficult.

Cognitive Map (Mental)Thoughts orbit bodily states: “What’s wrong with me?” “I can’t handle this feeling.” Sensation is misread as danger.

Inner Presence (Psychic)Awareness collapses into the body. The witness is lost in sensation. The soul confuses intensity with identity.

External Conduct

Work is disrupted by bodily preoccupation. Relationships strain under emotional reactivity. Habits skew toward constant self-monitoring, symptom checking, or avoidance.

Day-in-the-Life Vignette (Excess)

He wakes already scanning his body. A tight chest becomes panic. A headache derails the morning. Even minor discomfort feels catastrophic. The day is organized around managing sensation.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 7 AND c.slug = 'somatic_presence';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The body drops out of experience.

Internal Landscape

Somatic Base (Physical)The body feels distant, dull, or unreal. Sensations are muted or ignored. One may forget to eat, move, or rest.

Emotional Current (Vital)Emotion feels abstract or blunted. Feelings are described rather than felt. There is emotional flatness or delayed reaction.

Cognitive Map (Mental)Thought dominates. Decisions are made cognitively, often ignoring bodily signals. Fatigue or stress appears suddenly, without warning.

Inner Presence (Psychic)Awareness retreats upward, leaving the body under-inhabited. The soul experiences life at a remove.

External Conduct

Work is mentally driven but physically draining. Relationships feel distant. Habits neglect the body—poor sleep, irregular eating, lack of movement.

Day-in-the-Life Vignette (Deficiency)

She works through meals without noticing hunger. By evening, exhaustion hits like a wall. She realizes she has barely felt her body all day—only thoughts.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 7 AND c.slug = 'somatic_presence';

-- -----------------------------------------------------------------------------
-- D8 — Nine Enduring Emotions  (9 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (8, 'rati', 'Rati', 'रति', 'Love, Attachment, Delight', 'Rati is the centripetal force of the human heart—the gravitational pull toward beauty, connection, and union. It is not limited to romantic desire, though it certainly includes it. Rati is the soul’s fundamental “yes” to life: the warmth that draws a parent to a child’s sleeping face, the quiet pleasure of a garden coming into bloom, the devotional surrender of the bhakta before the divine. It is the emotional current that makes us reach toward what we find beautiful, and in that reaching, discover something essential about ourselves.', 1),
    (8, 'hasa', 'Hāsa', 'हास', 'Mirth, Laughter, Humor', 'Hāsa is the lightening energy of consciousness—the force that lifts, releases, and reminds us that the structures we build around our lives are not as solid as they seem. It is not merely the response to a joke. Hāsa is the cognitive capacity to perceive incongruity, the emotional willingness to delight in absurdity, and the social grace of shared vulnerability that laughter creates. In the classical view, it arises when expectations are subverted in a non-threatening way, and its function is to dissolve rigidity—in the body, in thought patterns, and in the fortress of the ego.', 2),
    (8, 'soka', 'Śoka', 'शोक', 'Sorrow, Grief, Loss', 'Śoka is the breaking open of the heart in the face of impermanence. It is the emotional acknowledgment that what we love can be taken, that what we build can crumble, that we ourselves are transient. Legend holds that the first poem—the Rāmāyaṇa—was born when the sage Vālmīki witnessed the killing of a bird and his raw grief spontaneously crystallized into rhythmic verse. The very word śloka (verse) derives from śoka (sorrow). In the classical view, grief is not merely something we suffer; it is something that creates—it gives birth to empathy, poetry, and ultimately to wisdom.', 3),
    (8, 'krodha', 'Krodha', 'क्रोध', 'Anger, Fury, Indignation', 'Krodha is the fire of the psyche—a high-energy response to perceived violation, injustice, obstruction, or betrayal. It is heat and movement, the emotional equivalent of a boundary drawn in the sand. In its dharmic form—kṣātra-krodha, the righteous anger of the warrior—it protects truth, defends the vulnerable, and refuses to tolerate what should not be tolerated. In its distorted forms, it burns indiscriminately, consuming the person who carries it as readily as it consumes its target.', 4),
    (8, 'utsaha', 'Utsāha', 'उत्साह', 'Enthusiasm, Heroic Energy, Resolve', 'Utsāha is the propulsive force of the psyche—the will to act, to overcome, to rise. It is not the shallow excitement of novelty but the deep, sustained energy that makes a person capable of enduring difficulty in service of something larger than themselves. In the classical schema, it is the emotional engine of the Vīra (heroic) Rasa—the quality that transforms an ordinary person into someone willing to meet the world’s demands with courage and stamina.', 5),
    (8, 'bhaya', 'Bhaya', 'भय', 'Fear, Anxiety, Vulnerability', 'Bhaya is the contraction of consciousness in the face of perceived threat. It is the organism’s oldest intelligence—the capacity to recognize danger and mobilize accordingly. But Bhaya is not only primal. It extends from the visceral panic of the body to the cognitive anxiety of the planner and the existential dread of the philosopher. In the classical framework, it reveals the fragility of egoic identity: we fear because we identify with something that can be lost.', 6),
    (8, 'jugupsa', 'Jugupsā', 'जुगुप्सा', 'Disgust, Moral Aversion, Repulsion', 'Jugupsā is the emotional recoil from what threatens bodily or moral integrity. It is the force that makes us turn away from decay, cruelty, and corruption—both physical and ethical. In its biological form, it protects against contamination. In its moral form, it serves as the foundation of ethical discernment, the visceral refusal to participate in what degrades. The classical tradition recognizes it as the root of both purity and prejudice, depending on whether it is guided by wisdom or by ignorance.', 7),
    (8, 'vismaya', 'Vismaya', 'विस्मय', 'Wonder, Astonishment, Awe', 'Vismaya is the opening of consciousness when reality exceeds its current frame. It is the emotion of the threshold—the moment when the known dissolves and something unexpected, vast, or incomprehensible appears. In children, it is the default setting. In adults, it is the door that keeps closing and must be deliberately reopened. The classical tradition regards Vismaya as the seed of both scientific inquiry and spiritual vision—the state in which the ego’s certainties crack open to admit the possibility of the truly Real.', 8),
    (8, 'sama', 'Śama', 'शम', 'Tranquility, Equanimity, Peace', 'Śama is the ground of being—the abiding stillness beneath all emotional weather. Championed by Abhinavagupta as the ninth and foundational Sthāyībhāva, it is not the absence of feeling but the presence of a witnessing awareness that allows all other feelings to arise and dissolve without disturbance. It is the rasa of the sage, the Sthita-prajña of the Gītā, the condition in which consciousness rests in its own nature rather than being swept along by its contents.', 9);

-- D8 pole descriptions (27 rows)
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Rati operates in equilibrium, there is a quality of warmth in the chest that is not grasping. The person experiences affection as something that flows outward without demanding return. Internally, thoughts about loved ones carry a tone of appreciation rather than anxiety. The body feels open—shoulders relaxed, breathing easy, a softness around the eyes. There is a natural attentiveness to beauty in small things: the way light falls across a table, the particular cadence of a friend’s laughter.

In relationships, this manifests as genuine care without possessiveness. The person can hold space for another’s independence without experiencing it as rejection. At work, equilibrium Rati appears as aesthetic sensitivity and a capacity for collaborative warmth—the colleague who remembers birthdays not performatively but because they actually noticed. In daily habit, there is an orientation toward nourishment: the meal prepared with attention, the evening walk chosen for its beauty rather than its efficiency.

She waters the herbs on the windowsill before checking her phone. The basil has put out new leaves overnight, and she runs a thumb along one, releasing its scent into the kitchen air. Her partner is still asleep. She makes tea for two—not because it was asked for, but because the act of preparing it is itself a small pleasure. The morning feels unhurried. There is nothing to prove.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 8 AND c.slug = 'rati';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Rati becomes excessive—rājasic in the Guṇa framework—love curdles into possession. The internal landscape shifts from warmth to a kind of anxious heat. Thoughts about the beloved become repetitive, circling: Where are they? What are they feeling? Do they still feel the same? The body tightens—a constriction in the solar plexus, a restless energy in the limbs that refuses to settle. The “you complete me” mentality takes hold, and with it, a fragile dependence that swings easily from adoration to jealousy.

Externally, excess Rati produces controlling behaviors dressed up as care. The partner who texts twelve times in an afternoon. The parent who cannot tolerate the child’s emerging autonomy. At work, it may appear as an unhealthy attachment to a mentor, a project, or an institution—an inability to separate self-worth from the object of devotion. Daily habits become organized around the beloved object: meals skipped, friendships neglected, the entire rhythmic structure of life deformed by the gravitational pull of a single attachment.

He has refreshed her social media profile four times in the last hour. She posted a photo with someone he does not recognize, and the pit in his stomach has not closed since. He drafts a casual text, deletes it, drafts another. His work sits untouched on the screen. The apartment is immaculate—he cleaned it this morning as a kind of offering, imagining her arriving, imagining her noticing. She has not called. The silence is not neutral; it is a verdict.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 8 AND c.slug = 'rati';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Rati is suppressed or depleted—the tāmasic state—the world loses its luster. Internally, there is a flatness: not active suffering, but an absence of warmth. The person may go through the motions of connection without actually feeling connected. Thoughts about others carry no emotional charge. The body feels dull, heavy, untouched—as though wrapped in a thin layer of insulation that prevents the world from reaching the skin. Beauty passes by unnoticed.

In relationships, deficient Rati manifests as emotional withdrawal that the person themselves may not recognize. They are present physically but absent in quality. They stop initiating contact, not out of anger but out of a vague sense that it does not matter. At work, there is competence without passion—tasks completed, deadlines met, but nothing sparks genuine interest. Daily habits become mechanical: eating for fuel, sleeping from exhaustion, the rituals of living stripped of their savor.

The sunset is reportedly beautiful tonight. His neighbor mentioned it. He glances out the window and registers the colors—orange, pink, a bruised purple along the horizon—the way one might register the time on a clock. Information received; nothing stirred. He turns back to the television. He cannot remember the last time something struck him as beautiful. He cannot remember the last time the absence troubled him.

───────────────────────────────────', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 8 AND c.slug = 'rati';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In equilibrium, Hāsa manifests as a lightness of being that does not deny difficulty but refuses to be crushed by it. Internally, the person carries a gentle background hum of amusement at the human condition—including their own participation in it. There is cognitive flexibility: the ability to hold two perspectives simultaneously and find the gap between them illuminating rather than threatening. The body reflects this—relaxed jaw, easy breathing, a readiness to smile that is not forced.

In relationships, equilibrium Hāsa is the capacity to laugh together without anyone being diminished. It is the self-deprecating humor that builds trust, the playful banter that keeps long partnerships alive, the ability to defuse tension with a well-timed observation rather than a confrontation. At work, it appears as creative intelligence—the capacity to see problems from unexpected angles. In daily life, it is the spirit of līlā—play—that makes ordinary tasks tolerable and occasionally delightful.

The meeting has gone badly. The client rejected the proposal, the timeline is ruined, and the team is sitting in shell-shocked silence. She surveys the wreckage of their carefully prepared slides and says, quietly, “Well, at least the font choice was impeccable.” A beat. Then the project lead snorts, and the tension in the room cracks open like an egg. They begin to problem-solve. The laughter did not fix anything. It made fixing things possible.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 8 AND c.slug = 'hasa';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Excessive Hāsa—rājasic mirth—turns laughter into a defense mechanism or a tool of dominance. Internally, there is a compulsive need to find the joke in everything, a restless discomfort with sincerity or stillness. Beneath the humor runs a current of anxiety: if I stop being funny, will anyone stay? The body is performative—loud gestures, exaggerated expressions, a voice pitched for audience rather than intimacy.

In relationships, excess Hāsa manifests as mockery disguised as wit, sarcasm that wounds while maintaining deniability (“I was just joking”), or an inability to be present during serious conversations. The person deflects vulnerability—their own and others’—with a punchline. At work, they may be the “class clown” who undermines authority or uses humor to avoid accountability. In daily habit, nothing is taken seriously enough to demand genuine engagement, and a creeping exhaustion develops beneath the performance.

His friends have stopped telling him important things. He learned about the diagnosis secondhand, a week after the fact. “We didn’t know how to bring it up,” they said. “You always turn everything into a bit.” He laughed when they told him this, because what else could he do? Later, alone, the laughter did not come. He sat with the silence and did not know what to put in it.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 8 AND c.slug = 'hasa';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Hāsa is deficient—the tāmasic state—life becomes unbearably heavy. Internally, everything is literal, weighty, consequential. The person cannot find the gap between expectation and reality where laughter lives; instead, every deviation from the expected is experienced as threat or failure. The body holds tension without release—clenched jaw, rigid posture, a face that has forgotten how to soften.

In relationships, deficient Hāsa produces a grim seriousness that makes others uncomfortable. The person is “no fun”—not because they are unkind, but because they have lost access to the playful register of human connection. At work, they become the colleague who takes every email as a crisis, every piece of feedback as an attack. Daily life is a succession of obligations approached with dutiful grimness. The capacity for delight has atrophied, and with it, a certain resilience—because without humor, there is no shock absorber between the self and the world’s relentless impacts.

Her daughter is doing a cartwheel in the living room and lands sideways on the couch cushions, legs flailing. The child looks up, grinning, expecting shared delight. She sees her mother’s face—attentive but unsmiling—and the grin fades. “What’s wrong, Mama?” “Nothing, sweetheart. That was good.” But the words are correct without being true, and the child, who is five and therefore the world’s most accurate emotional instrument, knows the difference.

───────────────────────────────────', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 8 AND c.slug = 'hasa';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In equilibrium, Śoka softens rather than destroys. Internally, there is a deep ache—located often in the chest, sometimes behind the eyes—that is painful but not unbearable. Thoughts move slowly, with a quality of tenderness. The person is acutely aware of what matters: the preciousness of time, the fragility of connection, the weight of things left unsaid. The body wants stillness and warmth—a blanket, a window to sit beside, the presence of another person who does not need to speak.

In relationships, equilibrium Śoka deepens capacity for empathy. The person who has grieved well—who has allowed sorrow its full passage—becomes someone others trust with their own pain. At work, it produces a quality of seriousness that is not grim but profound: the person who knows what matters and does not waste energy on what does not. In daily habit, there is a quality of ritual—the candle lit for the departed, the walk taken in the place that once was shared—that honors loss without being consumed by it.

It has been eight months since his father died. The acute pain has receded into something more like weather—a persistent atmospheric condition that colors everything without preventing function. This morning, folding laundry, he found one of his father’s handkerchiefs mixed in with his own shirts. He held it for a long time. He did not cry. He simply stood there, in the kitchen, holding the cloth, and let the absence be fully present. Then he folded it carefully and placed it in a drawer.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 8 AND c.slug = 'soka';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Excessive Śoka—rājasic sorrow—transforms grief from an experience into an identity. Internally, the person replays the loss compulsively, mining it for meaning or for evidence of injustice. There is a quality of self-pity that feeds on its own narrative: “Why me? Why this? No one understands.” The body is heavy but restless—unable to settle, unable to act. Tears come easily but bring no relief, because they are performed rather than released.

In relationships, excess Śoka becomes manipulative, even if unconsciously so. Sorrow is used to claim attention, to avoid responsibility, to maintain a special status as the one who has suffered. Others begin to feel burdened rather than compassionate. At work, productivity collapses not because of incapacity but because grief has become a reason not to engage with anything that might demand energy. Daily life constricts around the loss until nothing else is visible.

It has been three years, and she still introduces the topic within the first ten minutes of any conversation. Friends have started to edit themselves around her—not mentioning their own joys, their vacations, their children’s milestones—because her grief fills the room so completely that anything else feels like trespass. She notices the distance growing and interprets it as further proof of her abandonment. The sorrow has become a fortress. She does not recognize that she is also its prisoner.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 8 AND c.slug = 'soka';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficient Śoka—the tāmasic suppression of grief—produces a peculiar hardness. Internally, the person has sealed over the wound without cleaning it. There is no active pain, but there is also no depth. Thoughts about the loss are avoided, redirected, or intellectualized: “Everyone dies. It’s natural. I’ve moved on.” The body carries the unprocessed sorrow as tension—in the throat (the unshed tears), in the chest (the unlocked breath), in the shoulders (the weight that was never set down).

In relationships, deficient Śoka manifests as an inability to be present with others’ pain. The person becomes the one who changes the subject, offers solutions instead of empathy, or simply disappears when things get heavy. At work, they may be hyperproductive—grief converted into relentless doing—but the work has a brittle, driven quality that lacks inspiration. Daily life is efficient but hollow. The person functions, but does not feel. And because they do not feel, they do not grow.

His mother died six weeks ago and he has not taken a single day off. His manager expressed concern; he assured her he was fine. He is fine. He runs five miles every morning, eats clean, sleeps seven hours. His apartment is spotless. His inbox is clear. He has not opened the box of her belongings that sits in his closet. He plans to get to it eventually. Right now, there are more pressing things.

───────────────────────────────────', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 8 AND c.slug = 'soka';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In equilibrium, Krodha is precise and proportionate. Internally, there is a clear recognition that something has gone wrong—a violation of fairness, a breach of trust, a line crossed. The feeling is hot but focused: a fire in the belly rather than a conflagration. Thoughts are sharp and directed toward the specific injustice, not toward character assassination. The body is mobilized—upright, alert, energized—but not out of control.

In relationships, this manifests as the ability to say no clearly, to confront without cruelty, to draw a boundary and hold it without escalation. At work, it appears as the colleague who speaks up in the meeting when a bad decision is being made, who names the problem everyone else is tiptoeing around. In daily life, equilibrium Krodha is the energy that fuels activism, reform, creative destruction—the refusal to accept what ought to be changed, paired with the discipline to channel that refusal constructively.

She heard the comment clearly. It was directed at the intern—a remark about her accent, framed as a joke, delivered with a smile. The room laughed politely. She did not. In the hallway afterward, she stopped the speaker. “That wasn’t funny, and it wasn’t appropriate. She’s new and she can’t push back yet. I can.” Her voice was steady. Her hands did not shake. The anger was there—she could feel it, bright and clean in her sternum—but it was in service of something, and so it did not need to be loud.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 8 AND c.slug = 'krodha';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Excessive Krodha—rājasic anger—loses its precision and becomes a consuming force. Internally, the person is flooded: thoughts race, loop, and escalate. Every past grievance is recruited to support the present fury. The body runs hot—elevated heart rate, clenched fists, a jaw locked tight enough to ache. The anger feels righteous, which makes it particularly dangerous, because the sense of justification removes all internal brakes.

In relationships, excess Krodha creates scorched earth. The person says things that cannot be unsaid, deploys intimate knowledge as a weapon, and mistakes destruction for strength. At work, they become the colleague everyone walks on eggshells around—the one whose displeasure alters the atmospheric pressure of the entire office. Daily life is organized around grudges, resentments, and a running tally of slights that never reaches zero. The body pays the price: chronic tension, digestive issues, the slow erosion of cardiovascular health that accompanies sustained cortisol elevation.

He has composed the email three times, each version angrier than the last. The most recent one begins with “I find it astonishing that you would—” and climbs from there. His heart is hammering. He can feel the pulse in his temples. Some part of him—distant, quiet, easily overruled—knows that sending this will damage the relationship irreparably. But the fire wants out, and the fire feels like truth, and truth, he tells himself, should not be silenced. He hits send. The satisfaction lasts approximately ninety seconds.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 8 AND c.slug = 'krodha';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficient Krodha—the tāmasic suppression of anger—produces a dangerous docility. Internally, the person registers violations but immediately suppresses the response: “It’s not that bad. I’m overreacting. It’s not worth the conflict.” Over time, the suppressed anger does not disappear but converts—into resentment that leaks out sideways, into passive aggression, into psychosomatic symptoms. The body stores what the voice refuses to say: chronic headaches, lower back pain, a persistent tightness in the throat.

In relationships, deficient Krodha produces the person who never fights, never pushes back, never says what they actually think—and who is, consequently, never fully known. Partners experience them as pleasant but opaque. At work, they absorb unreasonable demands without protest, earning the label “reliable” while burning out invisibly. Daily life becomes a practice of accommodation so habitual that the person can no longer distinguish between genuine agreeableness and the inability to assert their own needs.

She said yes to the extra project. She said yes to covering the shift. She said yes to hosting Thanksgiving even though it was not her turn. Tonight, loading the dishwasher for the third time today, she feels something hot and formless rise in her chest. She pushes it down with a practiced efficiency that looks, from the outside, exactly like patience. But patience is a choice. This is a habit that has forgotten it was ever a choice at all.

───────────────────────────────────', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 8 AND c.slug = 'krodha';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In equilibrium, Utsāha is characterized by a lack of confusion and a readiness to sacrifice comfort for a higher purpose. Internally, there is a quiet confidence—not the loud bravado of the ego, but the settled certainty that the work matters and that one is capable of doing it. Thoughts are organized around goals but not enslaved to them. The body feels alive, energized, responsive—capable of sustained effort without the jittery quality of anxiety.

In relationships, equilibrium Utsāha appears as reliability—the partner who shows up, the friend who helps you move, the parent who maintains structure during chaos. At work, it is the quality that separates productive perseverance from mere busyness: the person who stays focused through setbacks, who treats obstacles as problems to solve rather than signs to quit. Daily life has a rhythm of purposeful activity balanced by genuine rest.

The grant deadline is in three days and the data set is incomplete. She has been working twelve-hour days, but there is no panic in it. She knows what needs to happen, she has a plan, and she trusts her capacity to execute it. At ten p.m. she closes the laptop, walks the dog, eats dinner. The work will be there tomorrow. She is not anxious about it. She is ready for it.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 8 AND c.slug = 'utsaha';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Excessive Utsāha—rājasic heroism—transforms drive into addiction. Internally, the person cannot stop. Rest feels like failure; stillness provokes anxiety. There is a grandiosity to the energy—a sense that they are indispensable, that the mission depends uniquely on their effort. Thoughts are relentless, future-oriented, strategic. The body runs on cortisol and willpower, ignoring signals of fatigue, hunger, and pain until they become crises.

In relationships, excess Utsāha produces the person who is always doing and never present. Their partners feel like items on a to-do list. At work, they become the “martyr-hero”—taking on everything, delegating nothing, and burning out spectacularly. Daily life is a relentless forward march that leaves no room for the contemplative, the receptive, or the tender aspects of being human.

He has not taken a vacation in three years. He mentions this as a point of pride at dinner parties, and does not notice the looks exchanged by the other guests. His wife has stopped asking him to slow down. His children have adapted—they have learned that Dad is a force of nature, always in motion, always building something. What they have not learned is what he looks like at rest. Neither has he.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 8 AND c.slug = 'utsaha';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficient Utsāha—the tāmasic state—is a profound loss of vitality. Internally, the person knows what they should do but cannot summon the energy to do it. There is no fire in the belly. Thoughts are vague, circular, without traction. The body feels heavy, sluggish, resistant to movement. The distance between intention and action has become an uncrossable gulf.

In relationships, deficient Utsāha manifests as passivity—the person who goes along with whatever is suggested, who has no opinions about where to eat or what to do, who has surrendered the initiative of their own life. At work, they do the minimum, not out of laziness exactly, but out of a dispiriting sense that nothing they do will matter. Daily life is not so much lived as endured.

The application has been sitting on his desktop for six weeks. It is half-completed. Every morning he opens it, reads the next question, and closes it. The deadline is tomorrow. He stares at the screen and feels nothing—not anxiety, not determination, not even disappointment. Just a vast, gray indifference that he has begun to mistake for acceptance.

───────────────────────────────────', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 8 AND c.slug = 'utsaha';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In equilibrium, Bhaya is healthy caution married to clarity. Internally, there is an alertness that sharpens perception without distorting it. The person recognizes real risks and responds proportionately. Thoughts are evaluative but not catastrophic. The body is watchful—a heightened readiness that enhances rather than overwhelms. There is even, in the classical view, a moral dimension: the person who fears violating dharma acts with conscience and care.

In relationships, equilibrium Bhaya appears as appropriate vulnerability—the willingness to acknowledge what is at stake without being paralyzed by it. At work, it is the quality that produces thorough risk assessment, careful planning, and the prudence to build margins of safety. In daily life, it ensures that the person locks the door, looks both ways, saves for the uncertain future—without being controlled by the possibility of catastrophe.

The biopsy results come back tomorrow. She is afraid. She notices the fear with a certain clarity: the tightness in her stomach, the way her mind keeps rehearsing worst-case scenarios. She lets the thoughts run without chasing them. She calls her sister—not for reassurance, but for company. They talk about the garden, about the neighbor’s new dog, about nothing in particular. The fear is still there when she hangs up. But she is not alone with it, and that makes it bearable.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 8 AND c.slug = 'bhaya';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Excessive Bhaya—rājasic fear—is anxiety unmoored from its object. Internally, the mind generates threats faster than it can evaluate them. Every email might contain bad news. Every unfamiliar sensation in the body might be the beginning of something terrible. Thoughts spiral into worst-case architectures of extraordinary complexity. The body is locked in sympathetic overdrive: elevated heart rate, shallow breathing, a persistent knot in the stomach that never fully unties.

In relationships, excess Bhaya produces controlling behavior born from the terror of loss. The person micro-manages their partner’s safety, their children’s activities, their own exposure to any situation that cannot be fully predicted. At work, they become the bottleneck—unable to delegate because trust requires a tolerance for uncertainty that they do not possess. Daily life shrinks to the size of what can be controlled, and even that small domain is surveilled with exhausting vigilance.

He checks the locks three times before bed. He has checked the stove twice. He sets two alarms because one might fail. Lying in the dark, he reviews tomorrow’s schedule for potential hazards: the highway merge, the meeting with the new client, the weather forecast. His wife’s breathing beside him is steady and slow. She is asleep. He envies this with an intensity that is itself a kind of fear—the fear that he will never be someone who simply rests.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 8 AND c.slug = 'bhaya';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficient Bhaya—the tāmasic or excessively rājasic suppression of fear—produces recklessness that masquerades as courage. Internally, the person has severed connection with the body’s warning signals. There is a numbness to risk that is not true bravery but a kind of dissociation. Thoughts do not engage with consequences because consequences feel abstract, remote, irrelevant.

In relationships, deficient Bhaya appears as emotional carelessness—the person who makes promises without considering whether they can keep them, who takes risks with other people’s wellbeing as readily as with their own. At work, it produces the high-risk decision-maker who is celebrated until the inevitable crash. Daily life has a quality of invulnerability that is, in fact, a refusal to acknowledge the truth that all living things are vulnerable.

He has not seen a doctor in seven years. His friends have mentioned it. His sister mentioned it pointedly after their father’s heart attack. He shrugs it off. He feels fine. He has always felt fine. The fact that “fine” includes the persistent chest tightness he has been ignoring for six months does not enter his calculations, because he has arranged his consciousness so that certain information simply does not arrive.

───────────────────────────────────', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 8 AND c.slug = 'bhaya';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In equilibrium, Jugupsā is viveka—discriminative wisdom. Internally, there is a clear sense of what aligns with one’s values and what does not. The feeling is not rage but recoil: a quiet, firm turning away from what is harmful or degrading. The body registers it as a subtle contraction—a pulling back of the hand, a narrowing of the eyes—that signals “not this.”

In relationships, equilibrium Jugupsā appears as healthy boundary-setting—the ability to say “This is not acceptable to me” without hatred, and to withdraw from toxic situations without needing to destroy them. At work, it is the ethical backbone: the person who will not falsify data, who walks away from the deal that requires compromised values. In daily life, it manifests as integrity—the alignment of conduct with conviction.

The contract is lucrative. The client is eager. But something in the arrangement does not sit right—a vagueness about the sourcing, an eagerness to skip the compliance review. She cannot point to a specific violation, but her stomach knows. She declines. The client is surprised. Her colleagues are puzzled. She does not have a compelling argument; she has something older and more reliable—a visceral refusal to participate in something that feels wrong.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 8 AND c.slug = 'jugupsa';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Excessive Jugupsā—rājasic aversion—becomes judgmentalism and contempt. Internally, the person carries a running commentary of moral superiority: other people’s choices are disgusting, their habits are offensive, their values are corrupt. The emotional register narrows to a persistent state of disapproval. The body is held tight, as though perpetually bracing against contamination.

In relationships, excess Jugupsā creates an atmosphere of conditional acceptance. Others feel perpetually evaluated, perpetually at risk of failing to meet the standard. At work, the person becomes the moral inquisitor—useful in small doses, unbearable in sustained proximity. Daily life is organized around avoidance: of certain foods, certain people, certain neighborhoods, certain ideas—a world that shrinks as the list of the intolerable grows.

He has opinions about the way his neighbor parks, the way his colleague chews, the way the barista’s tattoo is slightly crooked. He has opinions about the music at the grocery store and the grammar in the company newsletter. Each opinion arrives with a small jolt of revulsion, a tightening of the mouth, a mental note filed under “things that are wrong with the world.” He is not unhappy, exactly. He is fastidious. And he cannot understand why people find him exhausting.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 8 AND c.slug = 'jugupsa';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficient Jugupsā—the tāmasic state—produces a troubling moral flatness. Internally, the person has lost the capacity to feel revulsion at what ought to revolt. Ethical boundaries become negotiable, then invisible. The body does not register the warning signals that something is off. There is a numbness to degradation—one’s own and others’—that looks, from the outside, like extreme tolerance but is actually a failure of discrimination.

In relationships, deficient Jugupsā manifests as the inability to leave situations that are harmful—staying in abusive dynamics, tolerating exploitation, confusing acceptance with passivity. At work, it is the person who goes along with unethical practices because “everyone does it” and has lost the capacity to feel that this is not sufficient justification. Daily life drifts toward entropy—standards of self-care, integrity, and aspiration gradually eroding without the person noticing.

The joke at the dinner party is cruel—aimed at someone not present, someone vulnerable. She laughs with the others. Driving home, she replays the moment and searches for the discomfort she thinks she should have felt. It is not there. A year ago, it would have been. She wonders, briefly, where it went. Then the thought passes, and she turns on the radio.

───────────────────────────────────', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 8 AND c.slug = 'jugupsa';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In equilibrium, Vismaya is a quality of openness that informs perception without overwhelming it. Internally, there is a spaciousness—a willingness to be surprised, to not know, to encounter the world as though it had something new to show you. Thoughts move with curiosity rather than conclusion. The body opens: eyes widen, breathing deepens, the chest expands. There is a quality of presence—the person is fully here, because wonder only exists in the present tense.

In relationships, equilibrium Vismaya appears as genuine interest in the other—the capacity to be surprised by someone you have known for decades. At work, it fuels innovation and creative problem-solving: the mind that can wonder “what if” without immediately dismissing the unfamiliar. In daily life, it is the practice of attention that transforms the ordinary—the walk to the train station, the pattern of rain on glass—into occasions for quiet astonishment.

He is fifty-three and has walked this trail a hundred times. Today the fog sits in the valley like a lake of white, and the hills rise above it like islands. He stops. He has seen fog before. He has seen valleys. But this—this particular arrangement of moisture and light and silence—is unrepeatable, and he knows it. He stands there for several minutes, doing nothing productive, accomplishing nothing measurable, and returns home slightly different than when he left.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 8 AND c.slug = 'vismaya';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Excessive Vismaya—rājasic wonder—becomes a kind of spiritual or intellectual intoxication that avoids the demands of ordinary life. Internally, the person is perpetually dazzled—chasing peak experiences, consuming novelty, seeking the extraordinary while neglecting the essential. Thoughts are scattered and grandiose: everything is connected, everything is meaningful, everything is a sign. The body may feel floaty, ungrounded—disconnected from the practical reality of gravity and bills and other people’s needs.

In relationships, excess Vismaya produces the partner who is always elsewhere—entranced by a new idea, a new teacher, a new spiritual framework—while the dishes pile up. At work, it is the visionary who cannot execute, the dreamer who starts projects with evangelical fervor and abandons them when the wonder fades into the hard labor of follow-through. Daily life becomes a series of enthusiasms with no connective tissue.

She has started her fourth meditation practice this year. Each one was, at the beginning, a revelation—this is the one, this is the path, this teacher truly understands. Then the novelty wore off, and the practice became practice—repetitive, demanding, ordinary—and she moved on. Her altar has accumulated the artifacts of abandoned devotions: a mala, a singing bowl, a book of kōans she has not opened since March. The wonder was real. The commitment was not.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 8 AND c.slug = 'vismaya';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficient Vismaya—the tāmasic state—produces a cynicism that masquerades as maturity. Internally, the person has decided that they have seen it all, that nothing new is possible, that the world is exactly as dull as it appears. Thoughts are reductive: explanations that flatten mystery into mechanism, interpretations that refuse enchantment. The body mirrors this closure—narrow gaze, shallow breathing, a postural rigidity that says “I am not available to be moved.”

In relationships, deficient Vismaya manifests as a lack of curiosity about the inner life of others. The person has categorized everyone and everything, and new information is bent to fit existing categories rather than allowed to challenge them. At work, it produces the person who has done things this way for twenty years and cannot conceive of an alternative. Daily life is predictable, controlled, and—in the deepest sense—uninhabited. The lights are on, but no one is looking out the windows.

His grandson is showing him something on the phone—a video of the James Webb Space Telescope images, the deep field, galaxies layered like sediment in an ocean of time. “Look, Grandpa. That light has been traveling for thirteen billion years.” He glances at the screen. “Very nice,” he says, and returns to the crossword. The child’s wonder meets no surface in him from which to reflect. It enters and falls, like a stone into sand.

───────────────────────────────────', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 8 AND c.slug = 'vismaya';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In equilibrium, Śama is not manufactured calm but natural spaciousness. Internally, there is a quality of “enoughness”—a sense that nothing is missing, that the present moment is complete as it is. Thoughts arise and pass without demanding pursuit. Emotions move through the field of awareness like weather across a sky that is itself unmoved. The body is relaxed without being limp, alert without being tense—a state of restful readiness.

In relationships, equilibrium Śama appears as the capacity for non-reactive presence—the person who can sit with another’s pain without trying to fix it, who can receive criticism without collapsing, who can hold space for difficulty without becoming difficulty. At work, it is the quality of leadership that remains steady when everything else is in flux. In daily life, there is an unhurried quality—a willingness to be with what is, rather than compulsively arranging what should be.

The news is bad. The restructuring will eliminate her position. She hears this, and there is a moment—a familiar tightening in the chest, a flash of fear, the beginning of a narrative about unfairness. She notices these arrivals the way one notices birds landing on a wire: they are there, and then they will not be there. She takes a breath. She asks the necessary questions. She does not perform calmness; she inhabits it. Later, walking to her car, she will feel the grief arrive, and she will let it come. But it will come to someone who is not made of grief, and that makes all the difference.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 8 AND c.slug = 'sama';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Excessive Śama—what might paradoxically be called rājasic tranquility—is the weaponization of calm. Internally, the person has repressed rather than integrated the other eight bhāvas. They appear serene, but the serenity is achieved through avoidance rather than through the honest encounter with anger, grief, fear, and desire that genuine Śama requires. There is a subtle smugness to it: “I am beyond all that.” The body may look relaxed, but there is a rigidity to the relaxation—a held quality that reveals the effort beneath the surface.

In relationships, excess Śama produces the infuriatingly unflappable partner who meets every conflict with detached equanimity and thereby denies the other person’s emotional reality. At work, it is the leader whose apparent calm is actually disengagement—who does not fight for what matters because fighting would disturb the performance of peace. Daily life becomes a spiritual performance: the meditation cushion, the measured tone, the carefully curated absence of urgency that mistakes itself for enlightenment.

“You never get upset about anything,” his wife says, and it is not a compliment. She has been trying to have this conversation for weeks. She is crying. He is sitting very still, nodding, breathing evenly, his face a mask of compassionate attention. He has read the books. He knows the framework. He is meeting her distress with “spacious presence.” What he is not doing is feeling anything. And she can tell. The empathy is structural, not emotional. The peace is a wall.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 8 AND c.slug = 'sama';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficient Śama—the tāmasic or chronically rājasic absence of inner peace—is perhaps the defining condition of contemporary life. Internally, the person has no access to stillness. The mind runs constantly—commentary, planning, rumination, evaluation—and there is no off switch. Silence is intolerable; it must be filled with noise, with screens, with stimulation. The body mirrors this perpetual motion: fidgeting, scrolling, eating without hunger, consuming without satisfaction.

In relationships, deficient Śama produces the person who cannot sit still long enough to listen, who is always reaching for the phone during conversation, who fills every pause with speech because silence makes them anxious. At work, they are perpetually busy but rarely productive in the deep sense—confusing activity with accomplishment. Daily life is a blur of stimulation: the podcast during the commute, the news during breakfast, the scroll before sleep. The person has not been genuinely quiet—internally, truly quiet—in so long that they have forgotten it is possible.

He reaches for the phone before his eyes are fully open. There are no urgent messages, but the act of checking has become the first movement of consciousness each morning—before thought, before intention, before the body has decided to inhabit the day. He scrolls through headlines while brushing his teeth. He listens to a podcast in the shower. He queues music for the drive. Somewhere beneath the layers of input, there is a person. He does not know what that person would think or feel in silence. He has not given them the chance to find out.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 8 AND c.slug = 'sama';

-- -----------------------------------------------------------------------------
-- D9 — Thirty-Three Transient States  (22 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (9, 'nirveda', 'Nirveda', NULL, 'Dejection: The Taste of Disillusionment', NULL, 1),
    (9, 'cinta', 'Cintā', NULL, 'The Anxiety-Despair Continuum', 'Cintā (Anxiety/Worry) and Viṣāda (Despair/Sorrow) form a natural continuum—the former is the agitated reaching for control over an uncertain future; the latter is what remains when that reaching has exhausted itself. Together, they represent perhaps the most universally recognized Vyabhicārībhāvas in contemporary life.

In equilibrium, Cintā is the adaptive signal that alerts us to genuine threats and galvanizes preparation. It is the tightening before a presentation, the alertness before a difficult conversation. It sharpens focus and mobilizes energy. In this form, it arises, serves its purpose, and dissolves—replaced, perhaps, by Harṣa (joy) or Dhṛti (steadfastness) when the challenge is met.

In excess, Cintā becomes the defining weather pattern of millions of modern lives. The mind’s forecasting mechanism, designed for genuine threats, runs continuously on imagined ones. The body stays in a state of low-grade activation—cortisol dripping steadily into the bloodstream like a leaking faucet. Sleep becomes elusive. The chest stays tight. Thoughts loop: ‘What if this happens? What if that happens? What did they mean by that?’', 2),
    (9, 'visada', 'Viṣāda', NULL, 'The Anxiety-Despair Continuum', 'Cintā (Anxiety/Worry) and Viṣāda (Despair/Sorrow) form a natural continuum—the former is the agitated reaching for control over an uncertain future; the latter is what remains when that reaching has exhausted itself. Together, they represent perhaps the most universally recognized Vyabhicārībhāvas in contemporary life.

In equilibrium, Cintā is the adaptive signal that alerts us to genuine threats and galvanizes preparation. It is the tightening before a presentation, the alertness before a difficult conversation. It sharpens focus and mobilizes energy. In this form, it arises, serves its purpose, and dissolves—replaced, perhaps, by Harṣa (joy) or Dhṛti (steadfastness) when the challenge is met.

In excess, Cintā becomes the defining weather pattern of millions of modern lives. The mind’s forecasting mechanism, designed for genuine threats, runs continuously on imagined ones. The body stays in a state of low-grade activation—cortisol dripping steadily into the bloodstream like a leaking faucet. Sleep becomes elusive. The chest stays tight. Thoughts loop: ‘What if this happens? What if that happens? What did they mean by that?’', 3),
    (9, 'alasya', 'Ālasya', NULL, 'Lethargy and Fatigue: The Weight of Inertia', 'Ālasya (Lethargy) and Glāni (Fatigue) together describe the experience of a consciousness that has lost its momentum. Ālasya is the unwillingness to begin; Glāni is the inability to continue. In the Guṇa framework, both are strongly colored by Tamas—the quality of inertia, heaviness, and resistance to change.', 4),
    (9, 'glani', 'Glāni', NULL, 'Lethargy and Fatigue: The Weight of Inertia', 'Ālasya (Lethargy) and Glāni (Fatigue) together describe the experience of a consciousness that has lost its momentum. Ālasya is the unwillingness to begin; Glāni is the inability to continue. In the Guṇa framework, both are strongly colored by Tamas—the quality of inertia, heaviness, and resistance to change.', 5),
    (9, 'sanka', 'Śaṅkā', NULL, 'From Apprehension to Panic', 'Śaṅkā is the preliminary stirring of suspicion—the sense that something is wrong, that the ground is not as stable as it appears. In its equilibrium form, it is the quiet voice that says ‘Check again.’ It slows impulsive decisions. It is the vigilance that keeps the organism safe. In excess, it becomes the chronic suspicion that poisons relationships and paralyzes decision-making. Every kindness conceals a motive. Every silence is a judgment. The world becomes a place of hidden threats.

Trāsa is the acute form—the full activation of the fear response, the adrenaline surge, the narrowing of consciousness to a single point of threat. In equilibrium, it is the lifesaving panic that moves the body before the mind has finished calculating. In excess, it is the panic attack in the grocery store, the terror that comes from nowhere and everywhere at once.

It starts in the checkout line. A tightness at the base of the throat, then a wave of heat rising up from the chest. His vision narrows. The fluorescent lights become impossibly bright. His heart hammers—he can feel it in his fingertips, in his ears. The person behind him is too close. The beep of the scanner is too loud. His thoughts fragment: Am I having a heart attack? What if I pass out? Everyone is looking at me. They aren’t looking at him. He knows this somewhere, in a small rational room at the back of his mind, but the door to that room has been slammed shut by the body’s alarm system. He abandons his cart and walks—carefully, deliberately, gripping the edge of ordinary composure—to his car. In the parking lot, with the engine running and the air conditioning blowing on his face, it passes. Fifteen minutes later, he feels foolish and ashamed. But his hands are still shaking.

The Somatic Base: Trāsa announces itself in the body first and foremost: racing heart, shallow rapid breathing, sweating palms, a sensation of the ground becoming unreliable. The body has declared a war that the rational mind did not authorize.

The Emotional Current: Raw, primal fear—the oldest emotion, the one that lives in the brainstem. In excess, it becomes untethered from any specific threat, free-floating, available to attach itself to anything.

The Cognitive Map: Thoughts become catastrophic and circular: ‘Something is very wrong. I am losing control. This will never end.’ The mind’s forecasting function has been hijacked by the alarm system.

The Inner Presence: At the psychic level, panic is a profound disconnection from the witnessing self. Consciousness collapses entirely into the content of fear. The ‘observer’—the part of us that can watch emotion without being consumed by it—has temporarily vanished. The spiritual lesson of Trāsa is precisely this: it reveals how tenuous our connection to the witnessing self can be, and how quickly we can lose it.

•  •  •', 6),
    (9, 'trasa', 'Trāsa', NULL, 'From Apprehension to Panic', 'Śaṅkā is the preliminary stirring of suspicion—the sense that something is wrong, that the ground is not as stable as it appears. In its equilibrium form, it is the quiet voice that says ‘Check again.’ It slows impulsive decisions. It is the vigilance that keeps the organism safe. In excess, it becomes the chronic suspicion that poisons relationships and paralyzes decision-making. Every kindness conceals a motive. Every silence is a judgment. The world becomes a place of hidden threats.

Trāsa is the acute form—the full activation of the fear response, the adrenaline surge, the narrowing of consciousness to a single point of threat. In equilibrium, it is the lifesaving panic that moves the body before the mind has finished calculating. In excess, it is the panic attack in the grocery store, the terror that comes from nowhere and everywhere at once.

It starts in the checkout line. A tightness at the base of the throat, then a wave of heat rising up from the chest. His vision narrows. The fluorescent lights become impossibly bright. His heart hammers—he can feel it in his fingertips, in his ears. The person behind him is too close. The beep of the scanner is too loud. His thoughts fragment: Am I having a heart attack? What if I pass out? Everyone is looking at me. They aren’t looking at him. He knows this somewhere, in a small rational room at the back of his mind, but the door to that room has been slammed shut by the body’s alarm system. He abandons his cart and walks—carefully, deliberately, gripping the edge of ordinary composure—to his car. In the parking lot, with the engine running and the air conditioning blowing on his face, it passes. Fifteen minutes later, he feels foolish and ashamed. But his hands are still shaking.

The Somatic Base: Trāsa announces itself in the body first and foremost: racing heart, shallow rapid breathing, sweating palms, a sensation of the ground becoming unreliable. The body has declared a war that the rational mind did not authorize.

The Emotional Current: Raw, primal fear—the oldest emotion, the one that lives in the brainstem. In excess, it becomes untethered from any specific threat, free-floating, available to attach itself to anything.

The Cognitive Map: Thoughts become catastrophic and circular: ‘Something is very wrong. I am losing control. This will never end.’ The mind’s forecasting function has been hijacked by the alarm system.

The Inner Presence: At the psychic level, panic is a profound disconnection from the witnessing self. Consciousness collapses entirely into the content of fear. The ‘observer’—the part of us that can watch emotion without being consumed by it—has temporarily vanished. The spiritual lesson of Trāsa is precisely this: it reveals how tenuous our connection to the witnessing self can be, and how quickly we can lose it.

•  •  •', 7),
    (9, 'capalata', 'Capalatā', NULL, 'Impulsiveness and Excitement', 'Capalatā (Impulsiveness/Agitation) and Āvega (Excitement/Agitation) are the states of a consciousness that has been accelerated beyond its capacity for integration. Capalatā is the scatter—the mind leaping from object to object without completing any circuit of attention. Āvega is the rush—the surge of energy that floods the system and demands immediate discharge.', 8),
    (9, 'avega', 'Āvega', NULL, 'Impulsiveness and Excitement', 'Capalatā (Impulsiveness/Agitation) and Āvega (Excitement/Agitation) are the states of a consciousness that has been accelerated beyond its capacity for integration. Capalatā is the scatter—the mind leaping from object to object without completing any circuit of attention. Āvega is the rush—the surge of energy that floods the system and demands immediate discharge.', 9),
    (9, 'amarsa', 'Amarṣa', NULL, 'Restrained Anger: The Slow Burn', 'Amarṣa is one of the most psychologically subtle of the Vyabhicārībhāvas. It is not the explosive anger of Krodha (which belongs to the Sthāyībhāvas). It is the anger that has been swallowed—the irritation, the impatience, the simmering resentment that sits just below the threshold of expression. It is the anger of the person who smiles while their jaw is clenched.

He sits in the meeting, nodding. His colleague—the one who took credit for the strategy he developed—is presenting it to the leadership team. The slides are his slides, reorganized. The language is his language, slightly paraphrased. His face is composed. His voice, when he speaks, is measured. But beneath the professional surface, a slow heat is building in his solar plexus. It is not rage—that would be dramatic, visible, addressable. It is something quieter and more corrosive: the hot, tight feeling of being unseen. He will not say anything about it. He will go home, be short with his partner for no apparent reason, and lie awake replaying the meeting with the things he should have said. The anger will not be expressed; it will be metabolized—slowly, inefficiently, into the tissue of his body and the texture of his sleep.

The Somatic Base: Tension concentrated in the jaw, shoulders, and solar plexus. A subtle heating of the face. The breath becomes shallow and held. The body is primed for action but forbidden to act.

The Emotional Current: A compound of anger, humiliation, and impotence. The drive is toward justice—toward being seen, acknowledged, credited—but the social context does not permit the direct pursuit of that drive.

The Cognitive Map: Rumination and rehearsal. The mind replays the offense and scripts alternative responses—what one could have said, should have said, might say tomorrow. These scripts are rarely enacted.

The Inner Presence: Amarṣa reveals the gap between social performance and authentic selfhood. At the psychic level, it is an invitation to examine where we have surrendered our voice in exchange for approval or safety. The spiritual lesson is about boundaries—the dharmic necessity of right speech, of speaking truth without violence.

•  •  •', 10),
    (9, 'garva', 'Garva', NULL, 'Arrogance: The Fortress of Self-Regard', NULL, 11),
    (9, 'asuya', 'Asūyā', NULL, 'Envy: The Mirror That Wounds', 'Asūyā is the transient state of seeing someone else possess what we desire—and feeling diminished by the comparison. In equilibrium, it is the healthy recognition of admiration, the aspirational pull that motivates growth: ‘I want what they have’ becomes ‘I will work toward what they have.’ In excess, it becomes corrosive—a constant measuring of oneself against others that poisons satisfaction with one’s own life.', 12),
    (9, 'vrida', 'Vrīḍā', NULL, 'Shame: The Contraction of Being Seen', 'Shame is perhaps the most socially powerful of all the Vyabhicārībhāvas. In its balanced form—what the tradition calls healthy Vrīḍā—it is the internal check that maintains social harmony and personal integrity. It is the flush of discomfort when we have crossed a boundary, the signal that our behavior has fallen below our own standards. Healthy shame is corrective; it brings us back into alignment.

In excess, shame becomes toxic—a pervasive sense of deficiency that is not about what one has done but about what one is. The body curls inward, the gaze drops, the voice diminishes. The person becomes a fugitive from visibility, because to be seen is to be exposed, and to be exposed is to be found wanting.', 13),
    (9, 'moha', 'Moha', NULL, 'Delusion: When the Map Replaces the Territory', 'Moha is the fog itself—the state in which consciousness has lost clarity about what is real. It is not stupidity; it is a specific distortion of perception in which desire, fear, or habit prevents accurate seeing. In the Guṇa framework, Moha is quintessentially Tamasic: it is the darkness that does not know it is dark.', 14),
    (9, 'smrti', 'Smṛti', NULL, 'Recollection: The Arrival of the Relevant Past', 'Smṛti is not mere memory. It is the spontaneous, unbidden arising of a relevant past experience in the field of present consciousness. It is the moment when something you forgot you knew suddenly surfaces, recontextualizing everything. In equilibrium, Smṛti serves as a bridge between past experience and present wisdom—the grandmother’s advice that returns, decades later, at exactly the right moment. In excess, it becomes rumination—the mind trapped in a loop of replaying past events, unable to release them. In deficiency, it produces the disconnection from one’s own history that characterizes certain forms of dissociation.', 15),
    (9, 'harsa', 'Harṣa', NULL, 'Joy: The Sunbreak', 'He is walking home from the grocery store, carrying bags in both hands, thinking about nothing in particular. The late-afternoon light is golden, slanting through the trees. A small girl on the sidewalk ahead of him is trying to teach her dog to shake hands. The dog, a scruffy terrier, has no interest in shaking hands and is instead trying to lick peanut butter off the girl’s other hand. She is laughing so hard she cannot stand up straight. And something in him cracks open. Not breaks—cracks open, like light through a seam. For three, maybe four seconds, the weight of the week—the unfinished project, the argument with his brother, the dental appointment he keeps postponing—all of it lifts. Not because it has been resolved, but because the sheer, stupid, unearned beauty of a girl and a dog and golden light has momentarily revealed that the weight was never the whole story. He is smiling. He does not know why. By the time he reaches his apartment, the moment has passed. But something in the quality of the evening has been changed.', 16),
    (9, 'dhrti', 'Dhṛti', NULL, 'Steadfastness and Analytical Clarity', 'Dhṛti (Steadfastness/Contentment) and Mati (Analysis/Determination) represent the cognitive and volitional dimensions of clarity. Dhṛti is the capacity to hold steady in the midst of turbulence—to remain anchored when the waves of other Vyabhicārībhāvas crash against the psyche. Mati is the capacity for clear, penetrating analysis—the mind functioning at its highest discriminative capacity.

In equilibrium, these states provide the ballast that prevents the other transient states from capsizing the vessel of consciousness. A person with strong Dhṛti can experience Cintā (anxiety) without being swept away by it. A person with active Mati can encounter Moha (delusion) and see through it. In excess, Dhṛti can harden into rigidity—the person who refuses to feel, who ‘holds steady’ by suppressing rather than integrating. In excess, Mati can become hyperanalysis—the paralysis of a mind that dissects everything and participates in nothing.', 17),
    (9, 'mati', 'Mati', NULL, 'Steadfastness and Analytical Clarity', 'Dhṛti (Steadfastness/Contentment) and Mati (Analysis/Determination) represent the cognitive and volitional dimensions of clarity. Dhṛti is the capacity to hold steady in the midst of turbulence—to remain anchored when the waves of other Vyabhicārībhāvas crash against the psyche. Mati is the capacity for clear, penetrating analysis—the mind functioning at its highest discriminative capacity.

In equilibrium, these states provide the ballast that prevents the other transient states from capsizing the vessel of consciousness. A person with strong Dhṛti can experience Cintā (anxiety) without being swept away by it. A person with active Mati can encounter Moha (delusion) and see through it. In excess, Dhṛti can harden into rigidity—the person who refuses to feel, who ‘holds steady’ by suppressing rather than integrating. In excess, Mati can become hyperanalysis—the paralysis of a mind that dissects everything and participates in nothing.', 18),
    (9, 'vibodha', 'Vibodha', NULL, 'Awakening: The Moment the Fog Lifts', 'Vibodha is the transitional state of coming awake—not only from physical sleep, but from any form of unconsciousness, confusion, or Moha. It is the moment when the fog lifts and the landscape of reality becomes suddenly, startlingly clear. In the contemplative traditions, Vibodha describes the micro-awakenings that punctuate the path of inner development: moments when a familiar situation is suddenly seen with fresh eyes, when a longstanding pattern is recognized for the first time, when the ‘obvious’ becomes obvious at last.

She is in the middle of an argument with her mother—the same argument they have had, in different costumes, for twenty years. Her mother is saying the familiar words in the familiar tone. She is feeling the familiar tightening, preparing the familiar response. And then—without warning, without effort—something shifts. It is as if she has stepped two feet back from her own reaction and can see the whole pattern from the outside: the trigger, the escalation, the script, the predictable outcome. She sees her mother’s fear beneath the criticism. She sees her own defensiveness as a reflex, not a choice. The argument has not stopped—her mother is still talking—but something inside her has clicked into a different gear. She takes a breath. ‘Mom,’ she says, and her voice is different—not defensive, not conciliatory, just… clear. ‘I know you’re worried about me. I hear that.’ The silence that follows is new. Neither of them has been in this part of the conversation before.

•  •  •', 19),
    (9, 'jadata', 'Jaḍatā', NULL, 'Stupor: The Paralysis of Overwhelm', 'Jaḍatā is the state in which consciousness freezes. It is the deer in the headlights. It is the person who receives devastating news and simply… stops. Not crying, not screaming, not processing. Just stopped. The body is present; the mind has gone somewhere the body cannot follow.

The doctor is still talking, but the words have become sounds without meaning. ‘Biopsy’ was the word that did it—or maybe it was ‘lymph node.’ She is not sure. She is aware, distantly, that she is sitting in a chair, that the light in the office is blue-white, that there is a framed diploma on the wall she cannot read. Her hands are in her lap. They do not feel like her hands. The doctor pauses, asks if she has questions. She shakes her head. She has a thousand questions, but they are trapped behind a wall of glass. She walks to her car. Puts the key in the ignition. Sits. The parking lot is very ordinary—trees, other cars, a woman loading groceries into a trunk. The ordinariness of it is shocking. The world has not changed. Only she has changed. Or rather—she has not changed yet. She is in the space between the impact and the response, the silent gap between the lightning and the thunder. The thunder will come later. For now, there is only this strange, cottony stillness.', 20),
    (9, 'unmada', 'Unmāda', NULL, 'Temporary Insanity: When the Map Dissolves', 'Unmāda is among the most extreme of the transient states—the temporary dissolution of rational structure, the experience of a mind that has exceeded its own capacity for coherence. In the classical framework, it is recognized as a transient state, not a permanent condition—a crucial distinction. The mind can lose its moorings temporarily under extreme emotional pressure and find its way back. This normalizes experiences that contemporary culture often pathologizes—the ‘losing it’ that follows unbearable loss, the temporary dissociation that accompanies trauma, the altered states that arise in the extremity of grief or fear.

The phenomenological texture of Unmāda is distinctive: reality becomes porous. The boundaries between self and world, between memory and present experience, between the rational and the irrational, become permeable. Thoughts lose their usual logical sequence. Behavior becomes disconnected from intention. The person may laugh at inappropriate moments, speak in fragments, or act in ways that seem inexplicable to observers but carry a distorted internal logic.

•  •  •', 21),
    (9, 'autsukya', 'Autsukya', NULL, 'Longing: The Sweet Ache', 'Autsukya is the transient state of wanting what is absent—a person, a place, a time, a possibility. In equilibrium, it is the natural ache of love for someone who is away, the anticipation of a reunion, the aspiration toward a goal not yet reached. It gives life its forward motion, its sense of reaching toward.

In excess, Autsukya becomes obsessive longing—the inability to be present because the mind is perpetually elsewhere, dwelling on what is missing. The person cannot enjoy what they have because they are consumed by what they lack.

He stands at the kitchen window, watching the autumn light change. His daughter moved across the country three months ago for a job she loves. He is proud—genuinely, deeply proud. And he aches. Not all the time, not unbearably, but at moments like this—the golden hour, the quiet kitchen, the empty chair at the table where she used to sit and do homework with earbuds in, bobbing her head to music he pretended not to like. He picks up his phone, starts to text her, then puts it down. She is busy. She is building a life. The ache is not a problem to be solved; it is the emotional weight of love in the presence of absence. He lets it sit in his chest like a stone warmed by the sun. It is, he realizes, not entirely unpleasant. The ache itself is proof that what they had—what they still have—is real.

The Somatic Base: A pulling sensation in the chest, centered behind the sternum. The body feels oriented toward something beyond its immediate environment, as if leaning into a wind that only it can feel.

The Emotional Current: A bittersweet compound of love and absence. The hunger is for reunion, for completion, for the closing of a gap. But in its balanced form, the ache itself is recognized as valuable—as evidence of the capacity to love.

The Cognitive Map: Thoughts oscillate between present and absent: memories of what was, imaginations of what could be. In balance, these thoughts are held lightly. In excess, they consume all available bandwidth.

The Inner Presence: Autsukya, in its deepest form, is the soul’s longing for the Absolute—the ‘divine homesickness’ that the Bhakti traditions recognize as the engine of spiritual aspiration. Every human longing—for a person, for a place, for a state of being—is understood as a surface expression of this deeper longing for wholeness, for reunion with the source.

•  •  •', 22);

-- D9 pole descriptions (20 rows)
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In its balanced form, Nirveda serves a vital function. It is the healthy disillusionment that follows the recognition of impermanence or the limits of worldly satisfaction. It is what a person feels after achieving a long-pursued goal and discovering that the satisfaction is thinner than expected. In classical thought, this is the gateway to Vairāgya—dispassion—and it can catalyze genuine spiritual inquiry. The question ‘Is this all there is?’ is not pathological when it arises naturally; it is the soul’s hunger for something deeper.

The Somatic Base: A gentle hollowness in the chest, as if something has been quietly removed. The body feels lighter but also emptier, like a house after the furniture has been moved out. There may be a faint ache behind the sternum—not sharp, but persistent.

The Emotional Current: A wistful quality, like watching rain on a window. There is sadness, but it is clean sadness—not bitter, not self-pitying. It carries a strange sweetness, the sweetness of letting go.

The Cognitive Map: Thoughts turn reflective: ‘What truly matters? What have I been chasing?’ There is clarity in the questioning, even if the answers have not yet arrived.

The Inner Presence: The soul is beginning to withdraw its investment from the surface play of life. This is the first stirring of genuine inquiry. At the psychic level, Nirveda is an invitation—the personality is being asked to release its grip on outcomes so that something deeper can emerge.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 9 AND c.slug = 'nirveda';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Nirveda becomes dominant, the healthy questioning collapses into chronic disengagement. The world loses its color. Nothing seems worth the effort. This is not clinical depression in the Western sense—it is a specific flavor of disillusionment that has curdled into cynicism. The person withdraws not into reflection but into resignation. The question ‘Is this all there is?’ becomes the statement ‘Nothing is worth anything.’

The Somatic Base: The body feels leaden. There is a persistent gravitational pull—it is difficult to sit up straight. The eyes lose their brightness. Food tastes flat. The limbs move as though through thick air.

The Emotional Current: The underlying hunger is for meaning, but the emotional tone has become one of contempt—contempt for the world’s offerings, contempt for one’s own past enthusiasms. There is a bitter edge to the emptiness now.

The Cognitive Map: Thoughts crystallize into nihilistic narratives: ‘People are just performing. Relationships are transactional. Success is an illusion.’ These thoughts carry a false authority because they contain a grain of truth—but they have hardened into ideology.

The Inner Presence: The soul’s invitation to deeper inquiry has been refused. Instead of passing through disillusionment into genuine wisdom, consciousness has become stuck in the doorway, refusing to enter the next room and unwilling to go back.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 9 AND c.slug = 'nirveda';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Nirveda is absent where it should be present, the person remains perpetually invested in surfaces. They lack the capacity for disillusionment because they lack the capacity for genuine reflection. Every setback is rationalized, every disappointment reframed as ‘a learning experience’ before it has been properly felt. This produces a brittle optimism—a relentless positivity that fears its own shadow.

The Somatic Base: A surface-level buoyancy that never quite reaches the depths. The body stays busy—always moving, always productive—but there is a hollowness beneath the activity, like a balloon that looks full but contains only air.

The Emotional Current: An unacknowledged anxiety runs beneath the cheerfulness. The person is afraid that if they stop, if they question, the ground will give way.

The Cognitive Map: Reflexive positivity: ‘Everything happens for a reason. I just need to keep going. Thinking too much is the problem.’ The mind has learned to deflect any thought that might lead to genuine questioning.

The Inner Presence: The soul’s invitations are being systematically ignored. The disillusionment that should catalyze growth is being suppressed by a personality that cannot tolerate emptiness. The spiritual consequence is stagnation dressed as progress.

•  •  •', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 9 AND c.slug = 'nirveda';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'It is 2:47 a.m. and she is awake again. The quarterly review is in eleven days. She has prepared. She knows the numbers. But her mind has found a new thread to pull: What if they ask about the Carter account? She rehearses the answer. Then rehearses it differently. The ceiling stares back at her, impassive. She picks up her phone, checks email—nothing new, of course—and puts it down. Her stomach is tight, a familiar knot just below the ribs. She tries breathing exercises from the app. They work for ninety seconds. Then: What if the breathing exercise isn’t working because the anxiety is justified? A new loop begins. By morning she will be exhausted, functional, and carrying the invisible weight of a night spent wrestling shadows.

In deficiency—where appropriate anxiety is absent—the person becomes reckless. Without Cintā’s alerting function, they walk into avoidable disasters with unearned confidence. They sign contracts without reading the fine print. They ignore warning signs in relationships. Their body lacks the low hum of protective vigilance, and their cognitive map is dominated by an assumption of safety that reality does not warrant.

•  •  •', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 9 AND c.slug = 'cinta';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'It is 2:47 a.m. and she is awake again. The quarterly review is in eleven days. She has prepared. She knows the numbers. But her mind has found a new thread to pull: What if they ask about the Carter account? She rehearses the answer. Then rehearses it differently. The ceiling stares back at her, impassive. She picks up her phone, checks email—nothing new, of course—and puts it down. Her stomach is tight, a familiar knot just below the ribs. She tries breathing exercises from the app. They work for ninety seconds. Then: What if the breathing exercise isn’t working because the anxiety is justified? A new loop begins. By morning she will be exhausted, functional, and carrying the invisible weight of a night spent wrestling shadows.

In deficiency—where appropriate anxiety is absent—the person becomes reckless. Without Cintā’s alerting function, they walk into avoidable disasters with unearned confidence. They sign contracts without reading the fine print. They ignore warning signs in relationships. Their body lacks the low hum of protective vigilance, and their cognitive map is dominated by an assumption of safety that reality does not warrant.

•  •  •', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 9 AND c.slug = 'visada';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Healthy Ālasya is rest. It is the body’s wisdom when it says ‘not now’—the natural conserving of energy after exertion. Healthy Glāni is the honest fatigue that follows genuine effort, the satisfying tiredness of a full day’s work. Both are signals from the Prāṇamaya Kośa—the vital-energy sheath—that resources need replenishing.

The Somatic Base: A pleasant heaviness in the limbs. The eyelids soften. The muscles release their holding patterns. There is no resistance to the tiredness—it is welcomed, like sinking into warm water.

The Emotional Current: A quiet satisfaction in having earned rest. The drive is temporarily quiescent, and there is no guilt in the pause.

The Cognitive Map: Thoughts slow naturally. The mind’s planning function dims. There is a willingness to let tomorrow handle tomorrow.

The Inner Presence: The psyche is cycling between activity and receptivity—the natural rhythm of consciousness breathing in and out.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 9 AND c.slug = 'alasya';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Ālasya and Glāni become chronic, they produce a distinctive quality of suffering that is often invisible to others. The person does not appear to be in crisis—they appear to be doing nothing. But the internal experience is one of being trapped in thick air, where every action requires enormous effort and every task seems to grow larger the longer it is contemplated.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 9 AND c.slug = 'alasya';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Healthy Ālasya is rest. It is the body’s wisdom when it says ‘not now’—the natural conserving of energy after exertion. Healthy Glāni is the honest fatigue that follows genuine effort, the satisfying tiredness of a full day’s work. Both are signals from the Prāṇamaya Kośa—the vital-energy sheath—that resources need replenishing.

The Somatic Base: A pleasant heaviness in the limbs. The eyelids soften. The muscles release their holding patterns. There is no resistance to the tiredness—it is welcomed, like sinking into warm water.

The Emotional Current: A quiet satisfaction in having earned rest. The drive is temporarily quiescent, and there is no guilt in the pause.

The Cognitive Map: Thoughts slow naturally. The mind’s planning function dims. There is a willingness to let tomorrow handle tomorrow.

The Inner Presence: The psyche is cycling between activity and receptivity—the natural rhythm of consciousness breathing in and out.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 9 AND c.slug = 'glani';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Ālasya and Glāni become chronic, they produce a distinctive quality of suffering that is often invisible to others. The person does not appear to be in crisis—they appear to be doing nothing. But the internal experience is one of being trapped in thick air, where every action requires enormous effort and every task seems to grow larger the longer it is contemplated.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 9 AND c.slug = 'glani';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In balance, Capalatā is spontaneity—the ability to respond quickly, to pivot, to seize an opportunity. Āvega in balance is healthy enthusiasm—the quickening of energy that comes with genuine interest or creative inspiration. Both serve the dynamic, responsive quality of a fully alive consciousness.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 9 AND c.slug = 'capalata';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'She has seventeen browser tabs open. She was writing a report, then remembered she needed to check a statistic, which led to an article, which led to a related podcast clip, which she bookmarked to listen to later but instead started now because the first thirty seconds were interesting. She picks up her phone to add a reminder, sees a notification from a group chat, responds to it, puts the phone down, and cannot remember what she was doing before. The report blinks on screen, half a paragraph completed. Her coffee is cold. She has been ‘working’ for two hours and has produced almost nothing, but the subjective experience is one of frantic busyness. Her mind is a pinball machine. Each new stimulus triggers a little burst of dopamine—not enough to satisfy, just enough to redirect. By evening she will feel drained and vaguely guilty, unable to point to a single thing she completed.

The Somatic Base: A buzzing, wired quality. The body feels restless—legs jiggle, fingers tap. There is energy but no channel for it. The nervous system is in a state of diffuse activation.

The Emotional Current: A hunger for stimulation that is never quite satisfied. Each new input provides a brief hit, then the hunger returns, sharper.

The Cognitive Map: The mind’s attention function has been fragmented. Thoughts arrive rapidly but shallowly. There is no depth of engagement, only breadth of stimulation.

The Inner Presence: The witnessing self is being drowned out by the noise of the surface mind. This is the Rajasic pattern of Vyabhicārībhāva behavior: transient states feeding more reactions, snowballing into restless agitation.

•  •  •', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 9 AND c.slug = 'capalata';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In balance, Capalatā is spontaneity—the ability to respond quickly, to pivot, to seize an opportunity. Āvega in balance is healthy enthusiasm—the quickening of energy that comes with genuine interest or creative inspiration. Both serve the dynamic, responsive quality of a fully alive consciousness.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 9 AND c.slug = 'avega';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'She has seventeen browser tabs open. She was writing a report, then remembered she needed to check a statistic, which led to an article, which led to a related podcast clip, which she bookmarked to listen to later but instead started now because the first thirty seconds were interesting. She picks up her phone to add a reminder, sees a notification from a group chat, responds to it, puts the phone down, and cannot remember what she was doing before. The report blinks on screen, half a paragraph completed. Her coffee is cold. She has been ‘working’ for two hours and has produced almost nothing, but the subjective experience is one of frantic busyness. Her mind is a pinball machine. Each new stimulus triggers a little burst of dopamine—not enough to satisfy, just enough to redirect. By evening she will feel drained and vaguely guilty, unable to point to a single thing she completed.

The Somatic Base: A buzzing, wired quality. The body feels restless—legs jiggle, fingers tap. There is energy but no channel for it. The nervous system is in a state of diffuse activation.

The Emotional Current: A hunger for stimulation that is never quite satisfied. Each new input provides a brief hit, then the hunger returns, sharper.

The Cognitive Map: The mind’s attention function has been fragmented. Thoughts arrive rapidly but shallowly. There is no depth of engagement, only breadth of stimulation.

The Inner Presence: The witnessing self is being drowned out by the noise of the surface mind. This is the Rajasic pattern of Vyabhicārībhāva behavior: transient states feeding more reactions, snowballing into restless agitation.

•  •  •', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 9 AND c.slug = 'avega';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In its balanced form, Garva is healthy self-confidence—the quiet knowledge of one’s own competence, earned through genuine achievement. It is the pride that allows a craftsman to stand behind her work, a parent to feel satisfaction in their child’s growth, a student to present their research without apologizing for its existence. This is the pride that does not need an audience.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 9 AND c.slug = 'garva';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Garva becomes dominant, it constructs a fortress around the self-image. The person becomes hypervigilant to any challenge to their status or competence. Praise is expected; criticism is intolerable. Relationships become hierarchical—the arrogant person unconsciously ranks every interaction by who is ‘above’ and who is ‘below.’ The tragedy of excessive Garva is that it is always a defense against its opposite: the deeper the arrogance, the deeper the unacknowledged insecurity it protects.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 9 AND c.slug = 'garva';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'She opens Instagram and sees her former roommate’s post: a sun-drenched kitchen in the new house, the baby on the hip, the husband’s arm around the waist. She knows—rationally, clearly—that social media is a highlight reel. She knows her former roommate has her own struggles. But the feeling bypasses all of this. It arrives in the stomach first: a sinking, a tightening. Then the thoughts: Why does everything come so easily to her? What am I doing wrong? She puts the phone down, picks it up again, scrolls to another friend’s vacation photos. The same sinking. She closes the app and stares at the ceiling of her studio apartment. The apartment is fine. She liked it this morning. But after twenty minutes on social media, it has become evidence of her inadequacy.

The Somatic Base: A sinking in the stomach, a tightness in the chest. Sometimes a slight nausea—the body’s response to perceived diminishment. The shoulders hunch inward, as if trying to make the self smaller.

The Emotional Current: A compound of desire, inadequacy, and resentment. The hunger is not truly for what the other person has—it is for the feeling of ‘enoughness’ that their success seems to represent.

The Cognitive Map: Comparative thinking: an incessant, involuntary measuring of one’s life against curated images of others’ lives. The mind selects data that confirms inadequacy and filters out evidence of sufficiency.

The Inner Presence: Asūyā reveals where the self has been externalized—where identity has been made dependent on external markers rather than rooted in intrinsic being. The spiritual lesson is about Sva-dharma: the recognition that one’s own path, with all its apparent limitations, is the only path that can lead to genuine fulfillment.

•  •  •', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 9 AND c.slug = 'asuya';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'She rehearses the story three times before telling it at dinner, editing out the parts that make her look uncertain. When she laughs, she covers her mouth. When she disagrees, she phrases it as a question. In meetings, she sits slightly behind others, contributing only when directly asked, and even then qualifying every statement: ‘I could be wrong, but...’ ‘This might be a stupid question...’ She does not know that the pattern is visible. She thinks she is being modest, careful, appropriate. What she is actually doing is spending enormous energy ensuring that no one ever sees the unedited version of her. The cost is invisible but immense: a life lived at seventy percent of its natural volume, every genuine impulse filtered through the question, ‘What will they think?’', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 9 AND c.slug = 'vrida';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In its mildest, most balanced form, Moha is the natural confusion that accompanies genuine complexity. It is the bewilderment of standing at a crossroads without a clear map—a temporary state that, if tolerated, can give way to insight. In the Bhagavad Gītā, Arjuna’s Moha at the beginning of the battle is not pathological; it is the necessary confusion that precedes genuine understanding.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 9 AND c.slug = 'moha';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Moha becomes dominant, the person lives inside a story about reality rather than in reality itself. They may be deeply invested in a relationship that everyone around them can see is harmful. They may cling to a self-image that bears no relation to how they actually behave. They may pursue a goal that, if achieved, would not deliver what they imagine. The hallmark of excessive Moha is the imperviousness to feedback: evidence that contradicts the delusion is either ignored, reinterpreted, or aggressively rejected.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 9 AND c.slug = 'moha';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Harṣa in equilibrium is one of the most beautiful of all human experiences. It is the sudden, unexpected flash of joy that needs no reason and asks no permission. It arrives like a shaft of sunlight through clouds—briefly, intensely, gratuitously. A child laughing on a bus. A fragment of music overheard from a passing car. The smell of rain on warm asphalt. In these moments, the entire system—body, breath, mind, spirit—lights up for a few seconds, and the fundamental goodness of being alive becomes self-evident.

The Somatic Base: An expansion in the chest, as if the ribcage has suddenly found more room. The face softens. The eyes brighten. There is a lightness in the limbs—a momentary release from gravity. Sometimes, if the Harṣa is strong enough, goosebumps rise and the breath catches—these are the Sāttvikabhāvas, the involuntary psychophysical responses of genuine aesthetic-emotional experience.

The Emotional Current: Pure delight, unmixed with desire or possession. Harṣa is joy that wants nothing—it is not the satisfaction of getting what one wanted but the surprise of being touched by beauty or goodness without having sought it.

The Cognitive Map: Thoughts become spacious and appreciative. The mind’s usual commentary—judging, planning, comparing—falls silent for a moment. There is only the thought: ‘This. This is good.’

The Inner Presence: Harṣa is the closest the transient states come to the Sthāyībhāva of Rati (Love/Delight) and, ultimately, to the experience of Ānanda—the bliss that the Vedantic tradition places at the deepest core of the self. These brief flashes of joy are understood, in the contemplative traditions, as moments when the veils between the surface mind and the bliss-sheath (the Ānandamaya Kośa) thin momentarily. For a few seconds, we taste what is always there beneath the noise.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 9 AND c.slug = 'harsa';

-- -----------------------------------------------------------------------------
-- D10 — Paths of Engagement  (4 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (10, 'karma_yoga', 'Karma Yoga', NULL, 'The Path of the Doer', '"You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions." — Bhagavad Gītā 2.47

Karma, in its deepest sense, means action—any action, physical or mental. Karma Yoga is the discipline of performing that action selflessly, without attachment to its results, offering the fruits of one’s labor to something larger than the ego. The Bhagavad Gītā frames this as the most universally applicable path: nobody can live in a body and the world without doing actions. Even a renunciate living in a Himalayan cave must perform actions, and thus some degree of Karma Yoga is essential to every human life.

The Doer’s engagement with reality is fundamentally kinesthetic. It is the path of those who think with their hands, who process experience through movement and productivity. The question that drives the Karma Yogi is not “What is true?” or “What do I feel?” but “What must be done?” When this faculty is balanced, it produces the experience the Gītā calls niṣkāma karma—selfless action that flows naturally, without the friction of personal agenda.', 1),
    (10, 'jnana_yoga', 'Jñāna Yoga', NULL, 'The Path of the Observer', '"Even those who are considered the most immoral of all sinners can cross over this ocean of material existence by seating themselves in the boat of divine knowledge." — Bhagavad Gītā 4.36

Jñāna Yoga is the path of knowledge and wisdom—the most intellectual of the four paths, involving deep introspection, study of scriptures, and philosophical inquiry into the nature of reality and the Self (Ātman). The Observer’s engagement with reality is fundamentally cognitive. It is the path of those who process experience through analysis and discrimination, whose primary question is not “What must be done?” or “What do I feel?” but “What is real?”

The tradition identifies four pillars of Jñāna Yoga: Viveka (conscious, deliberate discrimination of real from unreal), Vairāgya (non-attachment to worldly possessions and ego), Ṣaṭ-Sampatti (six methods of mental and emotional training), and Mumukṣutva (the burning desire for liberation). Its methodology proceeds through three stages: Śravaṇa (hearing or receiving knowledge), Manana (deep reflection and logical analysis), and Nididhyāsana (direct experiential realization).', 2),
    (10, 'raja_yoga', 'Rāja Yoga', NULL, 'The Path of the Integrator', '"Elevate yourself through the power of your mind, and do not degrade yourself, for the mind can be the friend and also the enemy of the self." — Bhagavad Gītā 6.5

Rāja Yoga, the “royal path,” is the discipline of aligning body, breath, and mind through systematic practice. Codified by Patañjali in the Yoga Sūtras as the eightfold path (Aṣṭāṅga Yoga), it moves through eight limbs—from ethical conduct (Yama and Niyama) through physical posture (Āsana), breath regulation (Prāṇāyāma), sensory withdrawal (Pratyāhāra), concentration (Dhāraṇā), meditation (Dhyāna), and finally Samādhi, the transcendental state. Vivekananda regarded it as the surest and quickest method of attaining salvation, while acknowledging it requires immense faith in oneself as well as great physical and mental strength.

The Integrator’s engagement with reality is fundamentally regulatory. It is the path of those who process experience through the management of inner states. The driving question is not “What must be done?” or “What is true?” or “What do I love?” but “How do I align?”', 3),
    (10, 'bhakti_yoga', 'Bhakti Yoga', NULL, 'The Path of the Lover', '"Of those who fix their minds upon the Almighty, constantly glorify Him and possess great faith—such a one is considered a Bhakta." — Bhagavad Gītā 12.2

Bhakti Yoga is the path of devotion and love—the most emotionally accessible of the four paths, emphasizing a deep, personal relationship with the divine through prayer, chanting, singing, and surrender. The Lover’s engagement with reality is fundamentally relational. It is the path of those who process experience through the heart, whose primary question is not “What must be done?” or “What is true?” or “How do I align?” but “What do I love?”

The tradition describes a progression from Gauṇī Bhakti (devotion supported by external aids—rituals, images, mantras) to Parā Bhakti (supreme devotion, a spontaneous and unconditional love that transcends all forms). At its highest expression, Vivekananda taught, there is no difference between Parā Bhakti and the highest knowledge (Jñāna)—in the highest state of love, the lover loses himself in the Beloved and attains the state of Non-duality. Five emotional attitudes (Bhāvas) characterize the devotee’s relationship: peaceful reverence (Śānta), devoted service (Dāsya), sacred friendship (Sakhya), parental tenderness (Vātsalya), and the most intimate communion of lover and beloved (Mādhurya).', 4);

-- D10 pole descriptions (12 rows)
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The Somatic Base (Physical)

In equilibrium, the body of the Karma Yogi feels like a well-tuned instrument. There is a warmth in the limbs, a readiness in the musculature, a sense that the body is available for whatever the day requires. Energy does not spike and crash; it flows in a steady current from morning through evening. The hands feel purposeful. The breath is even and unnoticed. There is a particular quality of physical satisfaction that comes after meaningful labor—not the heaviness of exhaustion but a pleasant tiredness, the feeling of a body that has been used well.

The Emotional Current (Vital)

The emotional tone is one of quiet dignity. There is no desperate hunger for recognition, no anxious scanning of the environment for approval. The underlying drive is toward contribution rather than accumulation. When a task is completed, there is a brief moment of satisfaction—then the attention moves naturally to the next thing that needs doing. The emotional current feels like a river: directional, purposeful, but without turbulence.

The Cognitive Map (Mental)

The thoughts of the balanced Doer are characterized by a notable absence of self-referential noise. The inner monologue is task-oriented rather than ego-oriented. Instead of “How will this make me look?” or “What will I get from this?” the dominant thought pattern is simply “This is what needs to be done, and I am here to do it.” The Gītā’s instruction is precise: do your duty, but do not worry yourself with the results; even while working, give up the pride of doership; do your work in a regulated and disciplined manner.

The Inner Presence (Psychic)

At the soul level, balanced Karma Yoga is the experience of yajña—sacred offering. Every action becomes a form of worship, not in a grandiose sense but in the simple recognition that one’s labor is a participation in something larger than personal gain. The spiritual lesson is that freedom from the karmic cycle (karma chakra) comes not from inaction but from action performed without attachment—a paradox that resolves itself in the lived experience of flow.

Vignette: A Tuesday in the Life of the Balanced Doer

She rises at 5:45, not because an alarm forces her awake but because there is a rhythm to her mornings that her body has internalized. She makes coffee, packs her daughter’s lunch, and reviews her calendar—all with a kind of choreographic efficiency that has no audience. At work, she leads a contentious project meeting. Someone takes credit for her idea. She notices the flicker of irritation in her chest, acknowledges it, and lets it pass. The idea is in the world now; that is what matters. By evening, she is tired but not depleted. She folds laundry while listening to a podcast, and there is a curious contentment in the folding itself—the warmth of the fabric, the small geometry of making order from chaos. She does not need the day to have been ‘successful’ in any dramatic way. She did the work. That is enough.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 10 AND c.slug = 'karma_yoga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Karma dominates—when the will to act overrides all other faculties—the Doer tips into what contemporary psychology calls workaholism and what the Gītā recognizes as action driven by Rajas, full of passion, born of intense desire and attachment. The “I” becomes magnified: my benefit, my earnings, my reputation. This I-centric attitude, the Gītā warns, gives rise to a society of corruption, mistrust, and mental ill-health.

The Somatic Base (Physical)

The body of the compulsive Doer is a machine running hot. There is a persistent tension in the jaw, the shoulders, the lower back—the musculature of “holding everything together.” Sleep is shallow and dream-dense, often interrupted by middle-of-the-night surges of cortisol disguised as “ideas.” The hands are never still: checking the phone, tapping on the desk, reaching for the next thing to organize. There is a paradoxical fatigue—the body is exhausted, yet it cannot rest because stillness feels like failure.

The Emotional Current (Vital)

The underlying emotion is anxiety masquerading as productivity. If the Doer stops, a wave of guilt or existential dread rushes in. The emotional hunger is for validation through output. People are unconsciously categorized as “helpers” or “obstacles.” Relationships become transactional. There is a growing inability to receive—compliments feel hollow, rest feels selfish, leisure feels like stolen time.

The Cognitive Map (Mental)

The inner monologue is a relentless to-do list. The dominant thought pattern is: “If I don’t do it, nobody will.” or “The world will stop if I stop.” Every interaction is filtered through the lens of efficiency: “Is this conversation productive? Is this meeting necessary?” The concept of niṣkāma karma has been inverted; every karma is now loaded with personal stakes.

The Inner Presence (Psychic)

At the soul level, excess Karma is the experience of ahaṃkāra—the inflation of ego through identification with action. The spiritual lesson being presented (but not yet learned) is that one’s worth is not equivalent to one’s output. The ātman is obscured by the smoke of ceaseless doing, and the soul’s call for stillness is mistaken for laziness.

Vignette: A Tuesday in the Life of the Excess Doer

His phone buzzes at 4:47 AM with a notification he set for himself. Before his feet touch the floor, he is already composing emails in his head. Breakfast is eaten standing up, one eye on the news feed. He arrives at work twenty minutes early, feeling a small, tight pride in beating the traffic. By 10 AM, he has reorganized a colleague’s spreadsheet without being asked, responded to forty-two emails, and volunteered for a committee he has no time for. When his wife texts asking if he’ll make it to their son’s recital, he feels a sharp pang—not of guilt, exactly, but of resentment that someone is asking him to stop. At 11 PM, he is in bed with his laptop, checking metrics. He tells himself he’ll ‘just finish this one thing.’ The one thing takes ninety minutes. He sleeps fitfully, dreaming of spreadsheets.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 10 AND c.slug = 'karma_yoga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Karma is suppressed, the individual enters a state the tradition associates with Tamas—the darkness and crudeness born of ignorance, the force that binds through recklessness, laziness, and sleep. This is not simple tiredness. It is a fundamental collapse of the will to engage with the world, a condition in which even simple tasks feel like climbing a mountain.

The Somatic Base (Physical)

The body feels leaden, as though gravity has doubled. The limbs are heavy; the act of getting out of bed requires a kind of negotiation with oneself. There is a characteristic slumping in the posture—the shoulders roll forward, the chest caves slightly, the head drops. The musculature of the core feels weak, as though the body’s structural integrity has been compromised from within. Digestion slows. Breath becomes shallow and confined to the upper chest.

The Emotional Current (Vital)

The dominant feeling is not sadness but a kind of existential flatness—a world drained of urgency. There is no driving hunger, no fire of motivation. The emotional landscape resembles a desert: vast, quiet, and parched. Underneath this surface calm, there may be a buried shame—a sense that one should be doing more, that life is passing by—but even the shame lacks the energy to become a motivating force. The person feels like a victim of their schedule rather than the master of it.

The Cognitive Map (Mental)

The thoughts are characterized by a passive, defeatist narrative: “What’s the point?” or “Nothing I do makes a difference.” There is a collapse of agency—the belief that one is acted upon by the world rather than acting within it. Decision-making becomes agonizing because there is no internal compass of purpose to orient the choice. The inner monologue loops without resolution, like a record skipping.

The Inner Presence (Psychic)

At the soul level, deficient Karma is the experience of disconnection from one’s svadharma—one’s own rightful duty. The spiritual lesson is that the ātman expresses itself through engagement with the world, and when that engagement ceases, the soul’s voice grows faint. The call is to remember, as Kṛṣṇa told Arjuna, that even imperfect action taken from one’s own nature is preferable to perfect inaction.

Vignette: A Tuesday in the Life of the Paralyzed Actor

The alarm goes off at 7:00. She lies there. At 7:15, she picks up her phone and scrolls—not out of interest, but because the screen requires less effort than standing up. The emails from yesterday sit unanswered; the very act of reading them feels like pushing through wet sand. She eventually makes it to the kitchen, where the dishes from two days ago are still stacked. She knows she should wash them. She stares at them for a full thirty seconds, then pours a bowl of cereal and eats it on the couch. At her desk, she opens a document and reads the first paragraph three times without comprehension. The afternoon passes in a blur of half-started tasks and abandoned browser tabs. By evening, she feels a dull ache of shame—not for any specific failure, but for the general sense that she has been a spectator in her own day.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 10 AND c.slug = 'karma_yoga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The Somatic Base (Physical)

In equilibrium, the body of the Jñāna Yogi is characterized by a quality of stillness and composure. The posture is naturally upright—not rigid but alert, like a person who is genuinely listening. The nervous system operates with a refined sensitivity: the Observer notices subtle shifts in the body—a tightening in the stomach when something is not right, a lightening in the chest when truth is encountered—and uses these signals as data rather than being driven by them. The face tends toward a quality of calm attentiveness, the eyes focused but soft.

The Emotional Current (Vital)

The emotional tone is equanimity—not the suppression of feeling but the capacity to witness emotions without being captured by them. When someone insults the balanced Observer, they can intellectually deconstruct why that person is upset rather than taking it personally. There is a deep calm derived from understanding the “why” behind life events. The underlying drive is toward clarity rather than comfort; the Jñāna Yogi would rather know an uncomfortable truth than rest in a pleasant illusion.

The Cognitive Map (Mental)

The thoughts of the balanced Observer are characterized by precision and spaciousness. There is an inner “mental buffer”—a gap between stimulus and response in which discernment operates. The dominant cognitive activity is viveka: the continuous, deliberate sorting of the real from the projected, the essential from the superficial. Like the swan of classical metaphor that separates water from milk, the balanced intellect can perceive the ātman through the layers of conditioned experience. Knowledge serves liberation, not accumulation.

The Inner Presence (Psychic)

At the soul level, balanced Jñāna is the experience of progressive unveiling. Each insight into the nature of reality thins the veil of māyā (illusion) slightly, and the practitioner begins to sense the unity of Ātman and Brahman—not as an abstract proposition but as a quiet, growing certainty that permeates daily life. The spiritual lesson is that true knowledge is not information but transformation: it changes the knower.

Vignette: A Tuesday in the Life of the Balanced Observer

He sits with his morning tea, watching the steam curl. A thought about a workplace conflict surfaces, and he observes it with the same detachment he gives the steam—it rises, it dissipates. At his desk, a colleague presents a proposal that seems logically sound but carries a hidden assumption. He identifies the assumption not with hostility but with the care of a surgeon locating an obstruction. “This works,” he says, “if we assume the market doesn’t shift. What if it does?” The question clarifies the room. In the evening, he reads for an hour—not to escape but to refine his understanding of something he has been turning over for weeks. A passage in the book connects two ideas he hadn’t seen as related. He sets the book down and stares at the ceiling. It is not the excitement of ‘eureka’ but a quieter thing—the feeling of a puzzle piece finding its place.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 10 AND c.slug = 'jnana_yoga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Jñāna dominates, the Observer becomes trapped in the very instrument that was meant to liberate them. The intellect, rather than being a tool for discrimination, becomes an end in itself. This is the condition the tradition warns is the most difficult path precisely because the mind can convince itself of its own enlightenment without genuine transformation. The person acquires degrees, accumulates information, wins arguments—but none of this qualifies as jñāna in the scriptural sense, which requires not just learning but the dissolution of ego.

The Somatic Base (Physical)

The body of the excess Observer is often neglected—a vehicle deemed secondary to the mind. There may be chronic tension headaches, eye strain, and a disconnection from hunger and fatigue signals that have been overridden for so long that the body has stopped sending them at full volume. The posture becomes hunched over screens and books. Sleep is disrupted not by anxiety about tasks but by the mind’s refusal to stop processing. The body feels like an afterthought attached to a very busy head.

The Emotional Current (Vital)

The emotional landscape is characterized by a subtle but pervasive arrogance—the quiet conviction that understanding something intellectually is the same as having resolved it. Emotional experiences are immediately intellectualized: instead of feeling grief, the person analyzes the neuroscience of grief. Instead of experiencing joy, they categorize it. There is a growing inability to feel joy because one is too busy analyzing it. Intimate relationships begin to feel like debates; warmth gives way to correctness.

The Cognitive Map (Mental)

The inner monologue is relentless and argumentative. Every statement must be qualified, every claim examined, every feeling subjected to rational scrutiny. The dominant pattern is analysis paralysis—the inability to act because no amount of thinking ever produces perfect certainty. Conversations become competitions. The thought “I am right” has replaced the question “What is true?” The tradition compares this to a person carrying a lamp who becomes so fascinated by the lamp’s mechanism that they forget to look at the path it illuminates.

The Inner Presence (Psychic)

At the soul level, excess Jñāna is a particular form of spiritual materialism—accumulating knowledge as a possession rather than allowing it to dissolve the possessor. The ātman is hidden behind a fortress of concepts about the ātman. The spiritual lesson being offered is that viveka must be turned upon the intellect itself—the ultimate discrimination is the recognition that the mind is a tool, not the self.

Vignette: A Tuesday in the Life of the Imprisoned Intellect

He is in a meeting, and he is 100% sure he has the right answer. His mind spins with logical proofs. When a colleague disagrees, he feels a sharp pang of irritation at their ‘ignorance.’ He presents his case with devastating precision—citing data, referencing precedents, dismantling counter-arguments. He wins. And yet, as the room empties, he notices that no one makes eye contact with him. At lunch, a friend mentions feeling overwhelmed by a family situation. He immediately offers three solutions. The friend says, quietly, ‘I wasn’t asking you to fix it.’ He genuinely does not understand the distinction. That night, he lies awake, replaying the day’s conversations—not because they troubled him emotionally, but because he is constructing better arguments for tomorrow. He has become so trapped in the logic that he has lost the ability to connect with the human beings around him.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 10 AND c.slug = 'jnana_yoga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Jñāna is suppressed, the individual lacks the inner faculty of discernment. Without viveka, the mind cannot separate its own projections from reality, its conditioned reactions from genuine insight. The tradition describes this as avidyā—fundamental ignorance, not in the sense of lacking information but in the sense of mistaking the unreal for the real, the impermanent for the permanent, the non-self for the Self.

The Somatic Base (Physical)

The body of the person with deficient Jñāna often mirrors their mental confusion. There is a characteristic vagueness in the eyes, a quality of not-quite-being-present. The nervous system is reactive rather than discerning: the same physiological stress response fires for a genuine threat and for a social media argument. The body’s signals are neither recognized nor interpreted meaningfully—hunger, fatigue, and pain are noticed only when they become overwhelming.

The Emotional Current (Vital)

The emotional landscape is characterized by susceptibility. Without the discriminative faculty, the person is easily swayed by trends, social pressure, charismatic authorities, and emotional manipulation. There is a quality of being “tossed about” by others’ opinions, with no internal anchor to distinguish one’s own truth from the consensus. The emotional tone alternates between anxious conformity and confused resentment.

The Cognitive Map (Mental)

The thoughts are foggy, repetitive, and heavily influenced by external input. The person cannot distinguish between their own conclusions and something they heard on a podcast. Decision-making is outsourced: “What would so-and-so do?” replaces “What do I know to be right?” There is a particular vulnerability to groupthink and to the seductive certainty of ideology, which provides a ready-made cognitive map for those who have not developed their own.

The Inner Presence (Psychic)

At the soul level, deficient Jñāna is the condition of being asleep while appearing awake. The ātman is completely obscured by the undiscriminated flow of sensory input and borrowed opinion. The spiritual lesson is the beginning of the path itself: the recognition that “I do not know”—true mumukṣutva, the longing for liberation, begins with the honest acknowledgment of one’s own ignorance.

Vignette: A Tuesday in the Life of the Fogbound Mind

She wakes to her feeds. A wellness influencer says she should do a cold plunge; she feels a surge of conviction that this is what’s been missing. By noon, a coworker’s offhand comment about the economy sends her into a spiral of financial anxiety—though she cannot articulate, when pressed, what specifically she’s worried about. She has a vague sense that something is wrong but cannot locate it. In the afternoon, she sits through a presentation and nods along, absorbing the conclusions without questioning the premises. Later, her partner asks her opinion about a weekend plan. She says, ‘I don’t care, whatever you want.’ It is not indifference—it is the genuine inability to locate her own preference beneath the noise of everyone else’s.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 10 AND c.slug = 'jnana_yoga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The Somatic Base (Physical)

In equilibrium, the body of the Rāja Yogi is the most tangibly “known” of any path. There is an intimate relationship with the body’s architecture: the practitioner feels the quality of their breath, the alignment of their spine, the state of their digestion, not as medical data but as lived texture. The body feels “centered”—a word that is overused but here carries precise meaning: the felt sense of weight distributed evenly, of muscles neither gripping nor collapsing, of the nervous system in a state of alert relaxation. Energy is managed, not merely consumed; there is an understanding that sleep, food, and movement are not obligations but calibrations.

The Emotional Current (Vital)

The emotional tone is steadiness. Not the absence of emotion but a quality of resilience—the capacity to hold strong feelings without being capsized by them. In a chaotic environment, the balanced Integrator’s internal state remains steady, like a gyroscope that maintains its orientation regardless of how the ship pitches. There is a high degree of impulse control that does not feel like suppression but like sovereignty—the felt sense that one’s responses are chosen rather than compelled.

The Cognitive Map (Mental)

The thoughts of the balanced Integrator are characterized by a quality that Patañjali describes as ekāgratā—one-pointedness. The mind streams toward a single focus without distraction or interruption. This is not the furrowed concentration of effort but the easeful attention of a mind that has been trained. The inner monologue is relatively quiet; there is more awareness than commentary. When the mind does think, it does so clearly, without the overlapping chatter of competing narratives.

The Inner Presence (Psychic)

At the soul level, balanced Rāja Yoga is the experience of the mind becoming transparent to something deeper. As Kṛṣṇa explains, when the mind is restrained and detached from material desires, it experiences inner strength and peace; one can unite the self with the Almighty and attain a bliss that is beyond the experience of mundane situations. The practitioner begins to sense the Turiya—the fourth state of consciousness beyond waking, dreaming, and dreamless sleep—not as a mystical abstraction but as a quality of clarity that permeates all three.

Vignette: A Tuesday in the Life of the Centered Self

He wakes at 5:30 and sits for twenty minutes of meditation before the house stirs. He does not experience fireworks—just the gradual quieting of the night’s residual mental chatter, like a snow globe settling. Breakfast is deliberate: he eats slowly, noticing when he is full. On the commute, someone cuts him off in traffic. He feels the surge of adrenaline, notes it (‘there it is’), and lets it pass through him rather than feeding it with narrative. At work, a crisis erupts mid-morning—a product launch has a critical bug. While colleagues spiral, he feels the room’s energy like weather. He takes one slow breath, then says: ‘What’s the single most important thing to fix in the next hour?’ The question cuts through the panic. In the evening, he does thirty minutes of yoga—not for fitness but as maintenance, the way a musician tunes an instrument. He sleeps deeply, his nervous system already having processed the day’s friction through the morning’s practice.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 10 AND c.slug = 'raja_yoga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Rāja Yoga dominates, discipline hardens into rigidity. The tools of self-regulation—routine, restraint, practice—become ends in themselves rather than means to liberation. The Integrator tips into what might be called a “perfectionist’s burnout,” where the focus on purity and control extinguishes the very spontaneity and warmth that make life worth living.

The Somatic Base (Physical)

The body of the rigid ascetic is tightly controlled but curiously brittle. The posture is excellent but locked; there is a quality of holding that prevents the body from responding fluidly to the unexpected. The person may be extremely fit but lack the softness of real physical ease. Minor disruptions to routine—a late flight, a missed meal, an unavailable gym—produce disproportionate stress responses. The body has been disciplined but not befriended; it is a servant, not a partner.

The Emotional Current (Vital)

The emotional landscape is characterized by a cold, clinical detachment that the person may mistake for equanimity. There is a subtle judgment directed toward those who lack discipline—the colleague who eats fast food, the friend who sleeps in on weekends, the partner who cannot sit still for five minutes. Intimacy suffers because vulnerability feels like a loss of control. The emotional hunger is for perfection, which is, by definition, a hunger that can never be satisfied.

The Cognitive Map (Mental)

The inner monologue is a continuous audit of compliance: “Did I meditate long enough? Was my posture correct? Did I eat the right thing?” The mind, trained to monitor itself, becomes a merciless supervisor. There is a particular form of spiritual anxiety that emerges: the fear that one’s practice is “not enough,” that enlightenment is being thwarted by some subtle failure of discipline. The spontaneity that characterizes genuine spiritual opening is precisely what this rigidity prevents.

The Inner Presence (Psychic)

At the soul level, excess Rāja Yoga is the paradox of using the cage of discipline to seek freedom. The ātman cannot be reached through control alone—it requires surrender, which is the domain of Bhakti. The spiritual lesson being offered is that the final limb, Samādhi, is not an achievement of willpower but a grace that descends when the practitioner finally relaxes their grip.

Vignette: A Tuesday in the Life of the Rigid Ascetic

She rises at 4:30 AM—exactly 4:30, never 4:31—and begins her practice. Forty minutes of meditation, twenty minutes of prāṇāyāma, forty-five minutes of āsana. She eats a precisely measured breakfast of soaked almonds, fresh fruit, and warm water with lemon. At work, a team lunch is organized at a local restaurant. She declines. The food is not “clean” enough. She eats her prepared meal alone at her desk, feeling a familiar mix of superiority and loneliness. When her partner suggests a spontaneous weekend trip, she hesitates—it would disrupt her Saturday practice schedule. They go, but she is tense the entire time, mentally calculating how to fit in her routine at the hotel. On Sunday night, she cannot sleep. Not because the trip was stressful, but because her body, trained to expect a precise schedule, does not know what to do with the deviation. She lies in the dark, rigid and alert, the mind doing its auditing work: what was missed, what must be compensated for, how to restore order.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 10 AND c.slug = 'raja_yoga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Rāja Yoga is deficient, the individual lacks the internal architecture of self-regulation. Without discipline, the mind and body become mirrors of the environment—if the room is chaotic, the mind is chaotic; if the mood of the group shifts, the person’s state shifts with it. There is no gyroscope, no center.

The Somatic Base (Physical)

The body of the person with deficient Rāja Yoga is reactive and unpredictable. Energy levels spike and crash according to no discernible rhythm. Sleep is erratic—sometimes too much, sometimes too little, rarely restorative. The body feels like a vehicle with a faulty transmission: it accelerates when it should brake, stalls when it should move. There is a characteristic disconnection between what the body needs and what the person provides it; meals are skipped or binged, exercise is all-or-nothing, rest is replaced by collapse.

The Emotional Current (Vital)

The emotional landscape is turbulent. Without the regulatory framework of discipline, every stimulus produces a full-scale response. A critical email triggers a cascade of shame. A compliment produces a disproportionate high. The person cannot modulate their emotional volume; everything is either muted or overwhelming. Habits are impossible to maintain—not from lack of desire but from lack of the inner structure that converts desire into consistent action.

The Cognitive Map (Mental)

The thoughts are scattered, rapid, and unfinished. The inner monologue resembles a browser with forty-seven open tabs, each competing for attention. Plans are made and abandoned. Insights are glimpsed and lost. There is a particular frustration that accompanies this state: the person can see what they should be doing but cannot organize themselves to do it. The mind, without the training of dhāraṇā (concentration) and dhyāna (meditation), defaults to its unregulated state of compulsive fluctuation—what Patañjali calls citta-vṛtti, the turbulence of the mind-stuff.

The Inner Presence (Psychic)

At the soul level, deficient Rāja Yoga is the condition of a lamp in a windstorm. The light of the ātman is present but cannot be perceived because the flame of attention is perpetually guttering. The spiritual lesson is the most basic one of the path: that the mind, left to its own devices, is the enemy of the self—but the same mind, trained and directed, becomes its greatest friend.

Vignette: A Tuesday in the Life of the Scattered Self

He wakes at different times every day. Today it’s 8:20, twenty minutes after he should have left. He skips breakfast, grabs coffee, and drives in a state of low-grade panic that feels like his baseline. At his desk, he opens four applications simultaneously and accomplishes nothing substantial in any of them. He checks his phone sixty-three times by noon—not because anything important arrives but because the checking itself provides micro-hits of stimulation that fill the void left by sustained attention. He had planned to start a workout routine this week; the equipment is still in its box. By mid-afternoon, a colleague’s offhand frustration sends his mood plummeting. By evening, his partner’s enthusiasm for a cooking project lifts it. He is a weather vane, responding to every current. At midnight, unable to sleep, he scrolls through meditation apps—reading about discipline rather than practicing it—and falls asleep with the phone on his chest.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 10 AND c.slug = 'raja_yoga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The Somatic Base (Physical)

In equilibrium, the body of the Bhakti Yogi carries a quality of openness, particularly in the chest and the face. The breath is naturally deep and full—not regulated by technique but released by the simple fact of being at ease. There is a warmth to the physical presence that others register instinctively: people want to sit near this person. The body responds to beauty with real physiological signals—the skin prickles at a piece of music, the eyes moisten at an act of kindness, the chest expands with a sunrise. These are not exaggerated reactions but the body’s natural resonance when the heart is undefended.

The Emotional Current (Vital)

The emotional tone is gratitude—not the performative gratitude of journals and affirmations but the organic experience of finding the world, on the whole, beautiful and worth engaging with. The balanced Bhakti practitioner sees relationships as deep and meaningful and finds significance in the mundane: a cup of tea, a conversation with a stranger, the way afternoon light falls through a window. The underlying drive is toward connection—not clinging but genuine intimacy, the willingness to be touched by life without needing to control it.

The Cognitive Map (Mental)

The thoughts of the balanced Lover are characterized by a quality of receptivity. The mind is not passive but hospitable—it welcomes experience rather than fortifying against it. There is a natural tendency to see the divine in the particular: this person, this moment, this difficulty. The cognitive framework is relational rather than analytical; understanding comes not through dissection but through empathy and imaginative participation in the experience of others.

The Inner Presence (Psychic)

At the soul level, balanced Bhakti is the experience of being held—the sense that one is not alone in the universe, that there is a presence (however one names it) that receives one’s offerings of attention and returns something nourishing. The spiritual lesson is that surrender is not weakness but the highest form of strength: the ego’s dissolution into love is not a loss but the recovery of one’s true identity. As the tradition teaches, in the state of Parā Bhakti, love knows no bargaining, no fear, and no rival.

Vignette: A Tuesday in the Life of the Open Heart

She wakes to the sound of birds and lies still for a moment, feeling something she can only describe as ‘full.’ Not full of plans or energy but of presence. On the commute, she catches the eye of an elderly man on the bus and smiles without thinking. He smiles back. The small exchange warms her for an hour. At work, a junior colleague makes an error that creates extra work. Instead of irritation, she feels a flash of recognition—she made the same mistake once. She sits with the colleague and walks through the correction with the patient attention of someone who genuinely cares about the person, not just the output. In the evening, she lights a candle—not as a ritual but as a gesture toward the day’s end that feels right, like a period at the end of a sentence. She reads a poem aloud to no one in particular and finds her eyes wet. Not from sadness. From the simple, unexplainable fact of being alive and aware of it.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 10 AND c.slug = 'bhakti_yoga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Bhakti dominates, the heart’s openness becomes a liability. The person becomes emotionally volatile, tossed about by feelings the way the Jñāna-deficient person is tossed by opinions. There is a loss of grounding in practical reality—bills go unpaid, health is neglected, responsibilities are deferred because the person is overly focused on emotional or spiritual “highs.” The Gītā’s teaching that the Bhakta must control their senses and remain mentally composed in all situations is precisely the corrective needed here—and precisely what the excess Bhakti practitioner has not yet integrated.

The Somatic Base (Physical)

The body of the overwhelmed heart is porous—it absorbs the emotional atmosphere of every room. The nervous system is hypersensitive: crowds are exhausting, conflict is physically painful, even positive emotional intensity can produce a crash. There may be psychosomatic symptoms that mirror emotional states—chest tightness during relational tension, stomach distress during emotional processing. The boundary between one’s own somatic experience and someone else’s becomes blurred.

The Emotional Current (Vital)

The emotional landscape is a roller coaster without brakes. Joy is ecstatic, sorrow is devastating, love is all-consuming, disappointment is catastrophic. There is a quality of emotional addiction—the person seeks intensity rather than depth, confusing the height of the wave with the profundity of the ocean. Relationships become codependent; the person’s sense of self depends on the emotional feedback of others. When that feedback withdraws, there is a kind of existential free-fall.

The Cognitive Map (Mental)

The inner monologue is dominated by relational processing: “Do they love me? Did I say the wrong thing? What does this feeling mean?” The mind, rather than serving clarity, is co-opted by the heart’s turbulence. Practical thinking—logistics, planning, analysis—feels dry and burdensome. The person may develop a quiet contempt for the “mundane” aspects of life, which they experience as obstacles to feeling rather than containers for it.

The Inner Presence (Psychic)

At the soul level, excess Bhakti is the attachment to the experience of devotion rather than to the Beloved itself. It is Gauṇī Bhakti that has not yet matured into Parā Bhakti—devotion that still depends on external stimulation and emotional highs. The spiritual lesson is that true love, as Vivekananda taught, knows no bargaining; it persists regardless of what is returned. The overwhelmed heart must learn that devotion which requires constant emotional reward is not yet devotion—it is need.

Vignette: A Tuesday in the Life of the Overwhelmed Heart

She wakes feeling fragile—not from any specific event but from a dream she can’t remember that left a residue of longing. She checks her messages immediately, hoping for something warm. A friend’s casual response to her heartfelt text feels like a small rejection. She cries in the shower, then laughs at herself for crying, then cries again. At work, she pours herself into a mentoring conversation with such emotional intensity that the mentee becomes slightly uncomfortable. She notices and feels a wave of shame. She has trouble focusing on her quarterly report because numbers feel ‘soulless.’ In the evening, she puts on devotional music and loses herself in it for an hour, tears streaming—then realizes she forgot to eat dinner and the electricity bill is overdue. She pays it hastily, resenting the intrusion of the practical into what felt like a sacred evening. She sleeps poorly, the emotional residue of the day still swirling.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 10 AND c.slug = 'bhakti_yoga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Bhakti is suppressed, the individual lives in a world that is functional but drained of meaning. Life operates, but it does not sing. The tradition describes this as a spiritual aridity in which the heart’s natural capacity for connection, wonder, and devotion has been sealed off—sometimes by trauma, sometimes by the excessive dominance of one of the other paths (particularly an intellectualism that has trained the person to distrust feeling), and sometimes by the gradual erosion of neglect.

The Somatic Base (Physical)

The body of the person with deficient Bhakti often carries a quality of contraction, particularly in the chest and throat. Breathing is adequate but confined—the deep, expansive breaths of genuine emotional engagement are absent. There is a physical guardedness: the shoulders are slightly raised, the arms tend to fold across the chest, the facial muscles around the eyes are held tight. The body is functional—it works, it digests, it sleeps—but it does not resonate. Beauty passes through the visual field without producing a corresponding physical response.

The Emotional Current (Vital)

The emotional landscape is flat—not depressed in the clinical sense but arid. The person might describe themselves as “numb” or “apathetic,” though they are often highly functional. Everything is logical and operational, but nothing feels significant or beautiful. Relationships are maintained but not nourished; they are efficient rather than intimate. The underlying tone is a quiet cynicism: the sense that idealism is naivety, that hope is self-delusion, that the world is fundamentally mechanical rather than meaningful.

The Cognitive Map (Mental)

The thoughts are efficient but colorless. The inner monologue is dominated by logistics and analysis—the language of utility. “Is this useful?” replaces “Is this beautiful?” Aesthetic, spiritual, and emotional considerations are filed under “irrational” and dismissed. There is a particular resistance to vulnerability in thought—the mind avoids the open-ended, the uncertain, the mysterious, because these require a faculty (the heart) that is currently offline.

The Inner Presence (Psychic)

At the soul level, deficient Bhakti is the experience of exile from one’s own depths. The ātman is not absent but inaccessible—sealed behind layers of protective rationality or practical busyness. The spiritual lesson is that the soul speaks through the heart, and when the heart is closed, the soul’s communications—the sudden catch of beauty, the inexplicable tenderness, the longing for something unnamed—are mistaken for weakness and suppressed. The tradition teaches that all people will experience emotions such as love, compassion, and devotion at points along the journey, regardless of which path predominates. Bhakti deficiency is the resistance to this universal truth.

Vignette: A Tuesday in the Life of the Dry World

He is looking at a sunset. It is, objectively, spectacular—the sky is streaked with color, the light is doing extraordinary things to the ordinary buildings. He notices this the way he might notice a well-designed graph: with appreciation for the data but without being moved by it. His partner says, ‘Isn’t that incredible?’ He says, ‘Yeah, it’s nice.’ He means it. But the word ‘nice’ contains the entire poverty of his response—there is no resonance, no ‘Aha!’ His inner world feels like a desert. At dinner, his daughter tells him about a friendship drama at school. He listens, offers practical advice, and misses the fact that she didn’t want solutions—she wanted him to feel it with her. Later, alone, he picks up a novel his wife recommended. He reads ten pages, finds it ‘well-written but slow,’ and switches to a report for work. The truth he cannot yet see is that the novel is not slow—his heart is.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 10 AND c.slug = 'bhakti_yoga';

-- -----------------------------------------------------------------------------
-- D11 — Eightfold Refinement  (8 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (11, 'yama', 'Yama', NULL, 'The Ethical Ground', 'Ahiṃsā • Satya • Asteya • Brahmacarya • Aparigraha

The Restraints: How One Relates to Other Beings

“The yamas are nonviolence, truthfulness, refrainment from stealing, celibacy, and renunciation of unnecessary possessions.”

— Yoga Sūtra II.30

The yamas are the most external of the eight limbs, and they are placed first on the list for a reason that Patañjali makes emphatic: no yogic accomplishment is stable until these ethical restraints have been internalized. Vyāsa, the primary commentator, takes ahiṃsā—nonviolence—as the root of the entire set, comparing it to the footprint of an elephant that covers every smaller track. The other yamas—truthfulness, non-stealing, sexual restraint, and non-grasping—exist, in his reading, to support and deepen ahiṃsā. And Patañjali declares these to be mahāvrata, the “great universal vow,” not limited by class, place, time, or circumstance—as absolute a moral statement as the tradition produces.

But what do these restraints feel like from the inside? What is the lived phenomenology of a person whose ethical ground is stable, versus one in whom it has become rigid or one in whom it has eroded?', 1),
    (11, 'niyama', 'Niyama', NULL, 'The Personal Crucible', 'Śauca • Santoṣa • Tapas • Svādhyāya • Īśvara Praṇidhāna

The Observances: How One Cultivates the Inner Life

“Yoga in action is composed of austerity, self-study, and trustful surrender to Īśvara.”

— Yoga Sūtra II.1

If the yamas address how the aspiring yogī relates to the outer world, the niyamas turn the lens inward. These five observances—cleanliness (śauca), contentment (santoṣa), austerity (tapas), self-study (svādhyāya), and devotion to the Lord (Īśvara praṇidhāna)—constitute the personal crucible in which character is refined. Patañjali dedicates sixteen sūtras to the yamas and niyamas together—almost a tenth of his entire text, far more than he devotes to any other limb except samādhi—underscoring their foundational importance.

Three of the five niyamas—tapas, svādhyāya, and Īśvara praṇidhāna—also comprise kriyā-yoga, the “yoga of action,” presented at the opening of Chapter II. This overlap suggests that these three practices are not merely preparatory but constitute a complete spiritual path in their own right: the path of disciplined heat, honest self-examination, and surrender of the fruits of action. The remaining two—śauca and santoṣa—provide the container of cleanliness and contentment within which that inner fire can burn without consuming the practitioner.', 2),
    (11, 'asana', 'Āsana', NULL, 'The Embodied Seat', 'Steadiness and Comfort in the Body

“Posture should be steady and comfortable.”

— Yoga Sūtra II.46

Patañjali’s treatment of āsana is startlingly minimal: three sūtras, eight words. After dedicating sixteen sūtras to the ethical limbs, he gives the physical body less than one percent of his text. This is not dismissal; it is proportion. The posture serves the meditation, not the other way around. Sthira-sukham āsanam: the posture should be steady (sthira) and comfortable (sukham). That is the entire instruction. Vyāsa adds that the posture is perfected when effort ceases and the mind merges with the infinite—when the body, in other words, is no longer an object of attention but a transparent medium through which awareness flows.

Yet in the twenty-first century, āsana has become, for millions, the entirety of “yoga.” This extraordinary inversion—taking one-eighth of a system designed for the liberation of consciousness and treating it as the whole—is itself a symptom of deficiency in the other seven limbs. Understanding āsana’s proper phenomenology requires restoring it to its context.', 3),
    (11, 'pranayama', 'Prāṇāyāma', NULL, 'The Breath of Becoming', 'The Regulation of Vital Energy

“From this, the covering over the inner light is destroyed, and the mind becomes fit for concentration.”

— Yoga Sūtra II.52–53

Prāṇāyāma marks a threshold in the eightfold path. With the first three limbs, the practitioner has established an ethical foundation, cultivated personal discipline, and prepared the body. Now attention turns to the breath—the most intimate bridge between the voluntary and the involuntary, between the mind’s reach and the body’s depths. Patañjali defines prāṇāyāma as the regulation of inhalation and exhalation (II.49) and specifies that it has three aspects: exhalation (recaka), inhalation (pūraka), and retention (kumbhaka). He then makes a remarkable claim: that from the mastery of breath control, “the covering over the inner light is destroyed” (II.52). The breath, in other words, is not merely a physiological function; it is a veil. When it is regulated, something that was hidden becomes visible.', 4),
    (11, 'pratyahara', 'Pratyāhāra', NULL, 'The Inward Turn', 'The Withdrawal of the Senses from Their Objects

“Just as when the queen bee flies up, all the other bees fly up along with her, so when the mind is controlled, the senses are automatically controlled.”

— Vyāsa on Yoga Sūtra II.54

Pratyāhāra is the hinge of the entire system. The first four limbs are “external” (bahiraṅga); the last three are “internal” (antaraṅga). Pratyāhāra occupies the threshold between them. Its Sanskrit etymology reveals its function: prati (toward) + ā (from every direction) + hara (to withdraw, to carry)—“pulling the mind from every direction to a focal point.” It is the moment when the person who has been looking outward through the five senses begins, deliberately and with skill, to redirect that attentional energy inward.

This is not sensory deprivation. The senses continue to function; sounds are still heard, light still enters the eyes. But the mind ceases to follow the senses outward. Vyāsa’s metaphor is beautiful: just as when the queen bee settles down, all the other bees settle down with her, so when the mind is brought under control, the senses automatically become quiescent. The key insight is that the senses are not the problem; the mind’s habit of chasing them is.', 5),
    (11, 'dharana', 'Dhāraṇā', NULL, 'The Gathered Mind', '“Concentration is the fixing of the mind in one place.”

— Yoga Sūtra III.1

With dhāraṇā, we cross into the interior limbs—the antaraṅga—which Patañjali considers qualitatively different from all that precedes them. Dhāraṇā is the fixing of the citta—the mind-stuff—on a single object or location (deśa). This sounds deceptively simple. It is, in fact, the culmination of everything the preceding five limbs have prepared: an ethical foundation stable enough not to generate mental noise; a disciplined inner life that provides structure; a body that can sit without complaint; a breath that has been regulated; and senses that have been trained to follow the mind rather than drag it outward. Without these preparations, sustained concentration is simply not possible. The mind will find a reason—a physical discomfort, an unresolved ethical anxiety, a sensory itch—to break free.', 6),
    (11, 'dhyana', 'Dhyāna', NULL, 'The Unbroken Stream', '“Meditation is the one-pointedness of the mind on one image.”

— Yoga Sūtra III.2

The transition from dhāraṇā to dhyāna is not a change of method but a change of depth. Patañjali defines dhyāna as the unbroken flow (eka-tānatā) of cognition toward the object. In dhāraṇā, the mind is fixed on the object but breaks away intermittently; in dhyāna, the fixation has become continuous. The distinction is not qualitative but durational—yet that durational difference transforms the experience utterly.

When the mind rests on its object without interruption, a remarkable phenomenon occurs: the boundary between the knower and the known begins to thin. The meditator does not stop knowing; rather, the sense of being a separate entity who is performing an act of knowing begins to dissolve. The object of meditation becomes not something observed but something participated in. This is the threshold of samādhi.

T

h

e

e

x

c

e

s

s

o

f

d

h

y

ā

n

a

m

a

n

i

f

e

s

t

s

a

s

a

k

i

n

d

o

f

s

p

i

r

i

t

u

a

l

i

n

t

o

x

i

c

a

t

i

o

n

:

t

h

e

p

e

r

s

o

n

b

e

c

o

m

e

s

a

d

d

i

c

t

e

d

t

o

m

e

d

i

t

a

t

i

v

e

s

t

a

t

e

s

a

n

d

b

e

g

i

n

s

t

o

w

i

t

h

d

r

a

w

f

r

o

m

w

o

r

l

d

l

y

r

e

s

p

o

n

s

i

b

i

l

i

t

i

e

s

.

T

h

e

b

l

i

s

s

o

f

d

e

e

p

m

e

d

i

t

a

t

i

o

n

b

e

c

o

m

e

s

a

r

e

f

u

g

e

f

r

o

m

r

a

t

h

e

r

t

h

a

n

a

p

r

e

p

a

r

a

t

i

o

n

f

o

r

e

n

g

a

g

e

d

l

i

f

e

.

T

h

e

p

e

r

s

o

n

m

a

y

s

p

e

n

d

i

n

c

r

e

a

s

i

n

g

h

o

u

r

s

o

n

t

h

e

c

u

s

h

i

o

n

w

h

i

l

e

r

e

l

a

t

i

o

n

s

h

i

p

s

,

w

o

r

k

,

a

n

d

b

o

d

i

l

y

n

e

e

d

s

a

r

e

n

e

g

l

e

c

t

e

d

.

P

a

t

a

ñ

j

a

l

i

h

i

m

s

e

l

f

w

a

r

n

s

t

h

a

t

t

h

e

e

x

p

e

r

i

e

n

c

e

s

a

r

i

s

i

n

g

f

r

o

m

m

e

d

i

t

a

t

i

o

n

a

r

e

“

o

b

s

t

a

c

l

e

s

t

o

s

a

m

ā

d

h

i

”

w

h

e

n

t

r

e

a

t

e

d

a

s

e

n

d

s

i

n

t

h

e

m

s

e

l

v

e

s

(

I

I

I

.

3

7

)

—

t

h

e

s

i

d

d

h

i

s

,

t

h

e

p

o

w

e

r

s

,

t

h

e

v

i

s

i

o

n

s

a

r

e

a

l

l

d

i

s

t

r

a

c

t

i

o

n

s

i

f

t

h

e

y

b

e

c

o

m

e

o

b

j

e

c

t

s

o

f

a

t

t

a

c

h

m

e

n

t

.

T

h

e

d

e

f

i

c

i

e

n

c

y

o

f

d

h

y

ā

n

a

i

s

,

i

n

o

n

e

s

e

n

s

e

,

t

h

e

d

e

f

a

u

l

t

h

u

m

a

n

c

o

n

d

i

t

i

o

n

:

a

m

i

n

d

t

h

a

t

h

a

s

n

e

v

e

r

t

a

s

t

e

d

u

n

b

r

o

k

e

n

c

o

n

c

e

n

t

r

a

t

i

o

n

a

n

d

t

h

e

r

e

f

o

r

e

l

i

v

e

s

i

n

t

h

e

f

r

a

g

m

e

n

t

e

d

,

m

u

l

t

i

p

l

y

-

p

o

i

n

t

e

d

s

t

a

t

e

t

h

a

t

t

h

e

t

r

a

d

i

t

i

o

n

c

a

l

l

s

v

y

ū

t

t

h

ā

n

a

—

t

h

e

“

o

u

t

g

o

i

n

g

”

s

t

a

t

e

.

T

h

e

p

e

r

s

o

n

m

a

y

p

r

a

c

t

i

c

e

d

h

ā

r

a

ṇ

ā

d

i

l

i

g

e

n

t

l

y

b

u

t

n

e

v

e

r

c

r

o

s

s

t

h

e

t

h

r

e

s

h

o

l

d

i

n

t

o

t

h

e

s

u

s

t

a

i

n

e

d

f

l

o

w

t

h

a

t

t

r

a

n

s

f

o

r

m

s

c

o

n

c

e

n

t

r

a

t

i

o

n

i

n

t

o

m

e

d

i

t

a

t

i

o

n

.

T

h

i

s

i

s

o

f

t

e

n

a

m

a

t

t

e

r

o

f

p

a

t

i

e

n

c

e

a

n

d

a

c

c

u

m

u

l

a

t

i

o

n

:

t

h

e

t

r

a

n

s

i

t

i

o

n

f

r

o

m

d

h

ā

r

a

ṇ

ā

t

o

d

h

y

ā

n

a

i

s

n

o

t

v

o

l

i

t

i

o

n

a

l

b

u

t

e

m

e

r

g

e

n

t

,

a

r

i

s

i

n

g

w

h

e

n

t

h

e

c

o

n

d

i

t

i

o

n

s

a

r

e

r

i

p

e

.

I

t

c

a

n

n

o

t

b

e

f

o

r

c

e

d

,

o

n

l

y

p

r

e

p

a

r

e

d

f

o

r

.', 7),
    (11, 'samadhi', 'Samādhi', NULL, 'The Dissolution of the Knot', '“Samādhi is when that same dhyāna shines forth as the object alone and the mind is devoid of its own reflective nature.”

— Yoga Sūtra III.3

Samādhi is the culmination of the eightfold path and the ultimate purpose of human existence as Patañjali conceives it. It is not a practice; it is a state—the state that arises when practice has done its work. In samādhi, the distinction between the meditator and the object of meditation dissolves: the mind “shines forth as the object alone” and is “devoid of its own reflective nature.” The mind, in other words, has become so transparent that it has disappeared as a separate entity. What remains is pure awareness, aware of its object without the mediation of the ego-structure that normally claims authorship of every act of cognition.

Patañjali distinguishes two fundamental types. Samprajñāta-samādhi is “cognitive absorption”—a state in which awareness is absorbed in an object but retains some residual cognitive structure: vitarka (physical awareness of the object), vicāra (subtle awareness), ānanda (bliss), and asmitā (the minimal sense of I-ness). Asamprajñāta-samādhi is “supra-cognitive absorption”—the state in which even these last vestiges of cognitive structure dissolve, and awareness is aware only of itself: pure puruṣa, the soul, shining in its own nature. This is the final goal. This is kaivalya—absolute freedom, the wholeness of the self restored to itself.', 8);

-- D11 pole descriptions (22 rows)
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the yamas are integrated—not as external rules being obeyed but as dispositions that have soaked into the person’s character—the experience is one of extraordinary lightness. The ethical person does not spend psychic energy calculating whether to lie, whether to take what is not offered, whether to manipulate. That entire computational layer of social existence drops away, and with it, a background hum of anxiety that most people do not even realize they are carrying until it stops.

The Somatic Base. The body of someone living in yama-equilibrium carries an unusual quality of settledness. The jaw is not clenched. The shoulders do not creep toward the ears. There is a particular feeling in the chest—an openness, as though the sternum were a door left ajar—that comes from having nothing to hide. The gut is calm; there is no acid twist of concealed intention. Sleep is deep and uninterrupted, because the nervous system is not keeping vigil against the consequences of deception or aggression.

The Emotional Current. The dominant emotional tone is what the tradition calls maitrī—friendliness, a warm and uncomplicated goodwill that does not depend on whether others reciprocate. There is an absence of the predatory sharpening that accompanies competition and acquisition. Desire still arises—the person is not inert—but it arrives without the compulsive edge of grasping. There is enough, and the organism knows it at a cellular level.

The Cognitive Map. Thoughts are remarkably clean. The inner monologue is not consumed by strategic calculations: “What can I get away with? How do I position myself? What are they hiding?” Instead, the mind is freed for higher-order cognition—creativity, curiosity, genuine interest in others. Patañjali notes specific by-products: when truthfulness is established, one’s words acquire the power to actualize (II.36); when non-stealing is established, “all jewels approach” (II.37)—which the commentators interpret as spontaneous abundance, material and otherwise, flowing toward the person who has ceased grasping.

The Inner Presence. At the psychic or soul level, the person in yama-equilibrium is learning the first and most fundamental spiritual lesson: that the self is not enlarged by what it takes from the world. The false equation—more possessions, more status, more sensory experience equals more being—begins to dissolve. In its place, a quiet sufficiency emerges, a sense that one’s existence does not need external supplementation to be valid.

Vignette: A Tuesday in Equilibrium

She wakes before the alarm, not from anxiety but from a body that has rested deeply and is ready. At work, a colleague takes credit for her idea in a meeting. She notices the flicker of irritation—a heat behind the eyes, a tightening in the solar plexus—but it passes quickly, like a cloud across the sun. She does not need the credit to know the idea was hers. She does not need to diminish her colleague to feel whole. After the meeting, she mentions it simply and directly: “I’m glad the team liked the concept. I’d like to be acknowledged as the source.” No aggression, no manipulation, no subtext. In the evening, she eats a simple dinner and feels no compulsion to scroll through images of other people’s lives. Her own is sufficient. She reads for an hour, and the words on the page seem unusually vivid, as though her capacity for attention has been quietly expanded by the absence of internal noise.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 11 AND c.slug = 'yama';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the yamas are practiced with excessive rigidity—without the counterbalancing warmth of compassion and self-awareness—a distinctive distortion emerges. The person becomes morally brittle. The ethical principle, instead of serving as a foundation for genuine human connection, becomes a fortress from which others are judged and found wanting.

The Somatic Base. The body of the ethically rigid person is often tight in a particular way—not the raw tension of the anxious person but the controlled tension of the person who is holding themselves to a standard. The muscles along the spine are braced. The face carries a set expression, a kind of permanent mild disapproval. The breath is shallow and controlled, never fully surrendered. The body feels like a fist that has been clenched so long it has forgotten the shape of an open hand.

The Emotional Current. The dominant emotion is a cold, evaluative vigilance. There is righteous anger—frequently triggered, carefully managed, and inevitably leaking out as sarcasm, withdrawal, or passive judgment. Beneath the anger lies fear: the fear that relaxing one’s moral grip will lead to dissolution. The person often feels a chronic low-grade contempt for human weakness—others’ and, secretly, their own.

The Cognitive Map. The mind organizes the world into rigid moral categories. People are either “good” or “bad,” “serious” or “unserious.” Patañjali himself warns against this rigidity through the concept of pratipakṣa bhāvana (II.33)—when disturbed by contrary impulses, one should cultivate the opposite quality. But the rigidly ethical person applies this remedy only outward, never inward. The inner monologue becomes a prosecutorial brief against the world’s failings.

The Inner Presence. Spiritually, the excess of yama produces a subtle but devastating error: the person confuses moral performance with spiritual realization. They mistake the fence (the restraints) for the garden (the liberation the restraints are meant to protect). The ego, far from being diminished by ethical practice, has merely adopted a new costume—the costume of the righteous one.

Vignette: A Tuesday in Excess

He arrives at work early, as always. The first email of the morning contains a colleague’s careless joke—mildly off-color, nothing extraordinary—and he feels the familiar surge of moral indignation. He composes a reply that is technically polite but radiates disapproval. At lunch, his vegan meal sits on the table like a small monument to discipline. He does not mention his dietary choices, but he watches what others eat with an attention that is not quite curiosity. A friend cancels plans for the evening, citing tiredness. He does not say so, but he views this as a failure of commitment. Alone in his apartment, he reads a spiritual text, but his concentration is poor; the words seem to confirm what he already believes rather than opening any new door. He falls asleep with a faint sense of superiority, which he mistakes for peace.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 11 AND c.slug = 'yama';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the yamas are deficient—when the ethical ground has not been established or has been allowed to erode—the entire organism is destabilized. The person lives in a constant, low-grade state of predation and defense, because in the absence of ethical commitments, every interaction becomes a negotiation of power.

The Somatic Base. The body runs hot, driven by a sympathetic nervous system that never fully stands down. The gut is chronically unsettled—not the clean hunger of the ascetic but the gnawing emptiness of the acquisitive person who always feels as though they do not have enough. Sleep is fitful, haunted by the residue of the day’s manipulations. The eyes dart. The hands are restless, reaching for the phone, for the drink, for the next thing.

The Emotional Current. The dominant emotions are desire and fear, cycling in a feedback loop that the tradition calls rāga and dveṣa—attachment and aversion. There is a particular flavor of anxiety that accompanies ethical deficit: not the free-floating anxiety of the neurotic but the specific, situation-bound anxiety of the person who knows, at some level, that their behavior does not bear scrutiny. Patañjali locates this at the root of saṃsāra itself: the kleśas of ignorance, ego, desire, aversion, and clinging to life feed on each other in a vicious cycle (II.3–9).

The Cognitive Map. The mind is a restless calculator. Every conversation is filtered through the question: What can I gain? The inner monologue is populated by justifications: “Everyone does it.” “They would do the same to me.” “I deserve this.” The capacity for genuine empathy—the ability to feel another person’s experience as real—is progressively diminished, because empathy is inconvenient for a mind organized around extraction.

The Inner Presence. At the soul level, the deficiency of yama represents the deepest form of avidyā—the fundamental ignorance that mistakes the body and its appetites for the self. The person is, in Patañjali’s precise formulation, taking “the self, which is joyful, pure, and eternal, to be the nonself, which is painful, unclean, and temporary” (II.5). The tragedy is not moral failure in the conventional sense; it is a case of mistaken identity so thorough that the person does not even know they are suffering.

Vignette: A Tuesday in Deficiency

He wakes late, groggy from a night of poor sleep and too much screen time. At work, he inflates numbers on a report—not dramatically, just enough to make the quarterly figures look better than they are. He tells himself this is strategy, not dishonesty. At lunch, he flirts aggressively with a server, mistaking her professional friendliness for interest, using charm as a form of extraction. He buys something online he does not need, experiencing a brief neurochemical spike followed by a flatness that is becoming increasingly familiar. By evening, he is restless and slightly irritable, but he could not name the source. He pours a drink and opens his phone, swiping through content that briefly anesthetizes the low-grade hollowness he has come to think of as “normal.” The hollowness is not depression, exactly. It is the phenomenological signature of a life in which the ethical ground has dissolved, leaving nothing solid beneath the feet.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 11 AND c.slug = 'yama';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the niyamas are in equilibrium, the person lives with the quality of a well-tended fire: hot enough to purify, contained enough not to scorch. There is a daily rhythm of practice—whether meditation, study, movement, or service—that gives the days a structure that is felt in the body as stability and in the mind as clarity.

The Somatic Base. The body of someone practicing the niyamas in balance has a distinctive quality of radiance. Patañjali speaks of śauca producing “purity of sattva, cheerfulness, one-pointedness, mastery over the senses, and fitness for the vision of the self” (II.41). Physically, this manifests as a kind of cleanliness that goes beyond hygiene—the skin is clear, the eyes are bright, the digestion is strong. The body is neither indulged nor punished; it is maintained the way a skilled artisan maintains a fine instrument.

The Emotional Current. Santoṣa—contentment—provides the emotional baseline. This is not complacency or resignation but a deep trust that what has arrived by fate or effort is sufficient for the present moment. There is still ambition, still desire for growth, but it operates without the frantic edge of “not enough.” Tapas provides the fire: a willingness to stay with discomfort, to let difficulty be a teacher rather than an enemy. Svādhyāya adds honesty: the capacity to see one’s own patterns—the samškāras, the deeply grooved habits of mind—without flinching and without self-indulgence.

The Cognitive Map. The mind of the person in niyama-equilibrium is both reflective and surrendered. Svādhyāya ensures that self-examination is ongoing: the person regularly pauses to ask, “What story am I telling myself? What pattern am I repeating?” But Īśvara praṇidhāna ensures that this self-examination does not collapse into narcissistic self-absorption. There is a larger frame—call it the divine, the transcendent, the pattern of the whole—within which personal effort is nested and to which personal results are surrendered.

The Inner Presence. The spiritual lesson of the niyamas in equilibrium is the paradox of effort and surrender: that one must work with disciplined intensity and simultaneously release attachment to the outcomes. This is the heart of kriyā-yoga. The person is learning that the self is refined not by what it acquires but by what it burns away.

Vignette: A Wednesday in Equilibrium

She rises at 5:30, washes her face with cold water, and sits for twenty minutes of meditation—not because she feels like it (her bed was warm, her body stiff) but because the practice has become as natural as brushing her teeth. The meditation itself is unremarkable: the mind wanders, she brings it back, the mind wanders again. She does not judge this. Afterward, she reads a passage from a text she has been studying for months, a single paragraph that she turns over slowly, letting it interact with what she observed in her meditation. At work, a project she invested heavily in is cancelled. She feels the sting—a contraction in the chest, a flare of “This is unfair”—and she lets herself feel it fully, neither amplifying nor suppressing. By lunch, the sting has metabolized into something useful: a clearer understanding of what in the project was genuinely valuable and what was merely her ego’s investment. She eats slowly, tasting the food. In the evening, she practices āsana for forty minutes, not for the Instagram-worthy shapes but for the subtle proprioceptive conversation between breath and body. She goes to bed at a reasonable hour with the faint but genuine sense that the day, despite its disappointment, was complete.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 11 AND c.slug = 'niyama';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the niyamas tip into excess, the disciplined life becomes a prison of self-improvement. Tapas hardens into punitive austerity. Svādhyāya becomes obsessive self-analysis. Śauca mutates into a pathological need for purity that recoils from the ordinary messiness of human existence. The observances, meant to liberate consciousness, instead tighten the ego’s grip by giving it a spiritual project to manage.

The Somatic Base. The body of the person in niyama-excess is often lean to the point of austerity—not with the relaxed leanness of the naturally abstemious person but with the controlled leanness of someone who is at war with their own appetites. There is a rigidity in the posture that broadcasts discipline but not ease. The relationship with food has become fraught: every meal is a moral calculation. The body is treated not as a home but as a project—always being optimized, never permitted to simply be.

The Emotional Current. Contentment has been replaced by a relentless striving that wears the mask of spiritual aspiration. There is a chronic, low-grade dissatisfaction with the present state—a sense that one should be further along, more disciplined, more pure. The fire of tapas, unchecked by santoṣa, burns inward, producing not light but a dry, scorching self-criticism. Īśvara praṇidhāna—surrender to the divine—has been subtly co-opted by the ego: “I will surrender more perfectly than anyone else.”

The Cognitive Map. The mind is dominated by a perfectionist’s ledger: Am I meditating long enough? Am I eating purely enough? Am I reading the right texts? The self-study of svādhyāya has degenerated into a circular rumination in which every thought is examined, judged, and found wanting, generating further thoughts to be examined, judged, and found wanting. The person has become trapped in an infinite regress of self-observation.

The Inner Presence. The spiritual error of niyama-excess is a subtle but pervasive form of spiritual materialism: the accumulation of practices, disciplines, and attainments as though they were possessions. The ego, which the entire path is designed to dissolve, has merely relocated from the marketplace to the meditation cushion.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 11 AND c.slug = 'niyama';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the niyamas are deficient, the inner life lacks structure. The person lives reactively, buffeted by circumstances, without the steadying influence of regular practice, honest self-examination, or any sense of being situated within something larger than their own preferences. Patañjali identifies this state through his catalogue of distractions in I.30: disease, idleness, doubt, carelessness, sloth, lack of detachment, misapprehension, failure to attain a base for concentration, and instability. These are not abstract philosophical categories; they are the recognizable furniture of the undisciplined inner life.

The Somatic Base. Without the cleanliness of śauca, the body accumulates the residue of careless living—poor sleep patterns, inconsistent nutrition, a vague but persistent heaviness. Without the fire of tapas, the body tends toward lethargy, toward the inertia that the tradition identifies as tamas. The person feels perpetually “not quite right” in their body—not sick enough to seek treatment, not well enough to feel vital.

The Emotional Current. Without santoṣa—contentment—the emotional life is dominated by a restless wanting that can never quite identify its object. There is a chronic sense of something missing, combined with an inability to stay with any practice or inquiry long enough to discover what it might be. Moods swing with circumstances: good news produces elation, bad news produces despair, and the person has no inner shock absorber to modulate these oscillations.

The Cognitive Map. Without svādhyāya, the mind’s patterns go unexamined. The same reactions fire again and again—the same jealousies, the same avoidances, the same rationalizations—without ever being brought into the light of awareness. The person is, in the tradition’s language, asleep to themselves: living, as it were, in a waking dream composed of unquestioned assumptions.

The Inner Presence. Without Īśvara praṇidhāna—without any gesture of surrender to a reality larger than the ego—the person is trapped within the horizon of their own preferences. Life feels small, not because it is but because the lens through which it is being perceived admits only a narrow band of experience. The soul’s longing for transcendence—which the tradition considers the deepest human drive—finds no channel of expression and manifests instead as a vague spiritual homesickness that the person may not even recognize as spiritual.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 11 AND c.slug = 'niyama';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When āsana is in equilibrium, the body becomes what the tradition calls a “steady seat”—not an object of obsessive attention but a stable, comfortable platform from which the deeper work of yoga can proceed. The practitioner can sit for extended periods without distraction from physical discomfort. The body is strong but not rigid, flexible but not lax. It has been prepared, through regular practice, to sustain the stillness that the later limbs require.

The Somatic Base. The body feels inhabited—not as a possession to be displayed but as a home to be lived in. There is a proprioceptive awareness that extends throughout the musculature, a quiet aliveness in the tissues that the tradition associates with the free flow of prāṇa through the nāḍīs. Pain, when it arises, is met with curiosity rather than alarm. The body and the mind are in dialogue, not conflict.

The Emotional Current. The emotional tone of āsana-equilibrium is a steady, unspectacular contentment. The body has been given what it needs—movement, rest, nourishment, breath—and it is not demanding more. There is a particular quality of gratitude that arises when the body works well: a felt sense of the extraordinary privilege of having a functioning organism in which to experience the world.

The Cognitive Map. The mind is not preoccupied with the body. This is the crucial indicator of equilibrium: the body drops below the threshold of cognitive concern, freeing mental bandwidth for the subtler work of concentration and meditation. The practitioner is not thinking about their hamstrings during meditation; they are not planning their next workout during prayer.

The Inner Presence. At the soul level, āsana-equilibrium teaches the lesson that the body is a vehicle, not a destination. Through the practice of steady, comfortable posture, the practitioner learns a fundamental skill: the ability to remain physically still while the mind turns inward. This sounds trivial until one tries it. The body’s restlessness is a mirror of the mind’s restlessness; to quiet one is to begin quieting the other.

Vignette: The Body as Threshold

He finishes his morning practice—thirty minutes of postures, nothing dramatic—and sits on his cushion. His legs fold easily. His spine lengthens without strain. For a moment, as his breathing slows, the boundary between body and room seems to soften. He is not floating; he is simply not wrestling. The body is not pulling his attention downward into its demands. It is simply there, warm and quiet, like a candle in a still room. From this stillness, he can hear the quality of his own thoughts—not just their content but their texture, their pace, their emotional charge. The body, by becoming quiet, has become a doorway.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 11 AND c.slug = 'asana';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When āsana is practiced in excess—disconnected from the ethical and contemplative context of the other limbs—the body becomes not a vehicle but a project, not a threshold but a trophy. The posture practice, stripped of its spiritual purpose, collapses into athletic performance or aesthetic display. The practitioner pursues ever more advanced shapes, ever more impressive feats of flexibility and strength, while the mind remains as agitated and the heart as contracted as they were before the first downward dog.

The Somatic Base. The body of the āsana-excess practitioner is often impressively capable but subtly traumatized—joints pushed beyond their natural range, muscles chronically overworked, the nervous system perpetually in sympathetic activation from the intensity of the practice. There is a particular irony here: the body that was meant to become a “steady, comfortable seat” has instead become a source of chronic pain, because it has been treated as an instrument of achievement rather than a medium of awareness.

The Emotional Current. The relationship with the body is competitive and comparative. The practitioner watches others’ postures with an evaluative eye and experiences their own through the imagined gaze of an audience. The emotional tone oscillates between the brief elation of mastering a new shape and the frustration of failing at one. Āsana has become another arena for the ego’s relentless project of self-aggrandizement.

The Cognitive Map. The mind is body-obsessed: constantly monitoring physical sensation, planning the next practice, comparing today’s flexibility with yesterday’s. The deeper cognitive work of the yoga path—the examination of avidyā, the cultivation of viveka—is either ignored or treated as an afterthought. The practitioner may speak the language of yoga philosophy, but their actual cognitive center of gravity is the mirror.

The Inner Presence. The spiritual lesson that āsana-excess fails to learn is precisely the one the posture was designed to teach: that the body is temporary, the self is not. By inflating the importance of the physical form, the practitioner deepens rather than dissolves the fundamental confusion that Patañjali identifies as avidyā.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 11 AND c.slug = 'asana';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When āsana is deficient, the body becomes an obstacle rather than a support. The person cannot sit comfortably for meditation because the spine is weak, the hips are tight, the shoulders carry the tension of years of sedentary living. Physical discomfort is a constant low-level distraction, pulling attention away from the subtler dimensions of practice. The body, instead of dropping below the threshold of awareness, continually intrudes upon it.

The Somatic Base. The body in āsana-deficiency is characterized by stagnation: sluggish circulation, shallow breathing, chronic areas of tension that have calcified into structural patterns. There is a felt sense of heaviness—not the grounded heaviness of stability but the dragging heaviness of a body that has not been asked to move, to stretch, to express its full range. The person may not even be aware of how restricted their physical experience has become, because the restriction has been gradual.

The Emotional Current. There is a particular emotional dullness that accompanies physical neglect—a tamasic heaviness in which emotions are muffled, vitality is low, and the organism feels vaguely but persistently unwell. The absence of regular physical practice also means the absence of one of the most accessible entry points to present-moment awareness: the felt sense of the body in motion. Without this anchor, the mind is more likely to spin into rumination.

The Cognitive Map. Without the body’s grounding influence, the mind tends toward abstraction and dissociation. The person may develop an elaborate intellectual understanding of yoga philosophy while being unable to sit still for ten minutes. The split between theory and embodiment—knowing about consciousness while being alienated from one’s own body—is one of the most common and least discussed spiritual pathologies.

The Inner Presence. The soul’s lesson in āsana-deficiency is that the body is not an impediment to be transcended but a dimension of being to be integrated. Patañjali does not ask the yogī to escape the body; he asks the yogī to make the body steady and comfortable so that the spirit can use it as a seat. Without that seat, the spirit has nowhere to rest.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 11 AND c.slug = 'asana';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When prāṇāyāma is practiced in equilibrium, the breath becomes a teacher of extraordinary subtlety. The practitioner discovers that the breath is not something they do but something they participate in—a rhythm that connects the individual organism to the larger pulse of existence. Through careful observation and regulation, the breath slows, deepens, and eventually begins to reveal the energetic architecture of the subtle body.

The Somatic Base. The body enters a state of unusual integration. The diaphragm moves freely, and the breath flows into areas of the body—the lower back, the pelvic floor, the spaces between the ribs—that ordinarily lie below the threshold of awareness. There is a particular felt quality to a body in which prāṇa is moving freely: a warm, tingling aliveness that is distinct from either muscular effort or relaxation. The heartbeat slows. The parasympathetic nervous system comes into ascendancy. The body feels both alert and at rest—a combination that is almost paradoxical in ordinary experience.

The Emotional Current. The regulation of breath directly regulates emotion. This is not a spiritual claim but a neurological fact that the yogic tradition mapped millennia before modern affective neuroscience confirmed it. When the breath is slow, smooth, and rhythmic, the emotional landscape calms. Anxiety—which is, at its physiological root, a disordered breathing pattern—dissipates. In its place arises a quality of equanimity: not the absence of feeling but a spacious container within which feelings can arise and pass without overwhelming the observer.

The Cognitive Map. The mind, yoked to the breath, slows in tandem. The gap between thoughts widens. In that widening gap, something remarkable becomes perceptible: the mind’s own activity becomes an object of observation rather than an immersive experience. This is the beginning of the transition from identification with thought to witnessing thought—a shift that is preparatory to the internal limbs of dhāraṇā, dhyāna, and samādhi.

The Inner Presence. Prāṇāyāma in equilibrium teaches that awareness rides on the breath. As prāṇa expands, so does awareness. The practitioner begins to sense dimensions of their own being—subtle energies, interior spaces, the luminosity that Patañjali calls the “inner light”—that were previously occluded by the coarseness of ordinary respiration.

Vignette: The Breath Between Worlds

She sits after her morning practice, eyes closed, and begins a simple breath ratio: four counts in, sixteen counts held, eight counts out. Within minutes, something shifts. The room seems to recede. Not disappear—she can still hear the traffic, feel the texture of the cushion—but recede, as though the boundary of her body has softened and the sensory world has moved to a slightly greater distance. In the foreground: a luminous, buzzing stillness that is not silence but the sound of her own attention, refined to an unusual pitch. She can feel her heartbeat as a rhythmic event in a vast interior space. She can feel the quality of her thoughts before they become words. There is no effort involved; the effort was in the first five minutes of settling the breath. Now something is breathing her, and she is simply attending to the fact.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 11 AND c.slug = 'pranayama';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When prāṇāyāma is practiced in excess—with too much force, too much ambition, or without adequate preparation in the preceding limbs—the energetic system is destabilized. The tradition is unequivocal on this point: forced or premature breath work can be harmful. The subtle body, when overwhelmed by prāṇic energy it has not been prepared to conduct, responds with a characteristic set of disturbances.

The Somatic Base. The body becomes hyper-activated: racing heart, tingling extremities, spontaneous trembling, headaches at the crown of the head, pressure behind the eyes. Sleep is disrupted—not by anxiety but by an excess of energy that the nervous system cannot discharge. The person may feel electrically charged, as though the wiring of the body is carrying too much current. In extreme cases, there are involuntary physical movements—jerks, spasms, waves of heat or cold—that the tradition associates with improperly awakened kuṇḍalinī.

The Emotional Current. The emotional landscape becomes volatile. Euphoria alternates with irritability. The person may experience states of ecstatic bliss that are genuine but unsustainable, followed by crashes into agitation or despair. There is a quality of rawness to the emotional life, as though the protective membrane between the inner world and the outer world has been prematurely thinned.

The Cognitive Map. The mind in prāṇāyāma-excess may become grandiose: “I am having awakening experiences. I am ahead of schedule. I must practice more intensely.” Alternatively, it may become flooded with imagery, memories, or symbolic visions that the person lacks the container to integrate. Without the grounding of the yamas and niyamas, these experiences are not liberating but disorienting.

The Inner Presence. The spiritual danger of prāṇāyāma-excess is that genuine glimpses of subtler dimensions of being are misinterpreted by an unprepared ego. The person may confuse energetic phenomena for spiritual realization, mistaking the fireworks for the dawn.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 11 AND c.slug = 'pranayama';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When prāṇāyāma is neglected, the breath remains what it is for most people: an unconscious, unexamined, and remarkably disordered function. The modern person typically breathes shallowly, rapidly, and irregularly, using only a fraction of their lung capacity. This chronic underbreathing is both a symptom and a cause of the anxious, distracted, emotionally reactive mode of existence that the tradition identifies as the default condition of the unexamined life.

The Somatic Base. Without breath regulation, the body lives in chronic low-grade oxygen debt. The tissues are sluggish. The digestion is impaired. The nervous system is locked in sympathetic dominance—the perpetual fight-or-flight activation that modern life promotes and that the absence of prāṇāyāma practice does nothing to counter. Patañjali lists the somatic accompaniments of distraction in I.31: suffering, dejection, trembling, and disordered inhalation and exhalation.

The Emotional Current. The emotional life of the person who has never learned to regulate their breath is at the mercy of circumstances. Without the equanimity that steady breathing provides, emotions arise with full force and are experienced as overwhelming—not because they are inherently powerful but because the container is too small. Anxiety, in particular, is both generated and perpetuated by the shallow, rapid breathing patterns that prāṇāyāma is designed to correct.

The Cognitive Map. The mind without breath awareness is a mind without an anchor. It flits from thought to thought, driven by the same restless, irregular rhythm as the breath. The tradition’s metaphor is precise: as the breath goes, so goes the mind. Without prāṇāyāma, the mind has no way to calm itself except through distraction—seeking external stimuli to override the internal turbulence rather than addressing the turbulence at its source.

The Inner Presence. The “covering over the inner light” that Patañjali mentions in II.52 remains intact. The person has no access to the subtler dimensions of their own being—not because those dimensions do not exist, but because the coarseness of their breathing keeps the inner senses dulled. It is as though they are trying to hear a whisper while standing next to a jackhammer.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 11 AND c.slug = 'pranayama';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When pratyāhāra is in equilibrium, the person has developed what might be called sovereign attention: the ability to direct awareness by choice rather than by reflex. Sounds may arise in the environment, but the mind does not automatically lunge toward them. A craving may surface, but it can be observed without being obeyed. The person inhabits the same sensory world as everyone else but relates to it with a fundamental difference: the senses are in the service of the mind rather than the mind being dragged around by the senses.

The Somatic Base. The body in pratyāhāra-equilibrium has a quality of deep stillness even in the midst of activity. There is a particular inward quality to the gaze—the eyes may be open, but they are not scanning. The startle reflex is dampened. The body does not flinch at sudden sounds. There is a felt sense of an interior space—a vast, quiet chamber behind the senses—that has been accessed and is now available as a refuge.

The Emotional Current. The emotional life is characterized by an unusual stability. The person is not numb—they may feel deeply—but emotions arise as interior weather observed from a sheltered vantage point rather than as storms in which the person is a leaf. The tradition describes this as the development of a “healthy relationship with the foods of the senses”—the ability to receive sensory impressions without being consumed by them.

The Cognitive Map. The mind has developed a new capacity: the ability to choose its object of attention. This sounds trivially simple until one observes, honestly, how rarely it is the case in ordinary experience. The untrained mind is a stimulus-response machine, perpetually hijacked by whatever is loudest, brightest, or most emotionally charged. The mind trained in pratyāhāra can remain with a chosen object—a thought, a sensation, a question—in the presence of competing stimuli.

The Inner Presence. Pratyāhāra in equilibrium teaches the person that they are not their senses. This is a subtler lesson than it appears. Most people experience themselves as a bundle of perceptions: I am what I see, hear, taste, touch, and smell. Pratyāhāra creates an experiential gap between awareness and perception, and in that gap, the possibility of a deeper identity begins to emerge.

Vignette: The Crowded Room

He walks into the open-plan office. The room is a wall of noise: keyboards, conversations, the pneumatic hiss of the espresso machine. Six months ago, this would have fragmented his attention into a hundred pieces. Now, something different happens. He registers the sounds—all of them—and then, without effort, lets them recede. It is not that he has plugged his ears; it is that his attention has found its center of gravity. He sits down, opens his laptop, and within minutes is deep in a problem that requires sustained thought. The sounds continue—someone laughs, a phone rings, a chair scrapes—and they pass through his awareness like fish through clear water, leaving no disturbance. When a colleague taps his shoulder, he surfaces smoothly, without the jarring quality of being yanked from concentration. He was not absent; he was simply present in a different register.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 11 AND c.slug = 'pratyahara';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When pratyāhāra tips into excess, sovereign attention degrades into dissociative withdrawal. The person does not merely refrain from following the senses; they actively flee the sensory world. Human connection feels abrasive. Physical sensation is avoided. The body becomes a walled city with the gates shut, and the person inside becomes increasingly disconnected from the vitality and richness of embodied life.

The Somatic Base. The body feels distant, as though experienced through a pane of glass. There is a numbness that mimics equanimity but is actually avoidance. The person may lose touch with hunger, fatigue, or pain—not through mastery but through dissociation. The eyes have a glazed, unfocused quality. The body moves through space with an automaticity that lacks the aliveness of genuine presence.

The Emotional Current. The emotional life is flattened. The person has achieved not equanimity but anesthesia. Joy and sorrow alike fail to register with full force. Relationships suffer because genuine intimacy requires sensory and emotional availability, and the person in pratyāhāra-excess has traded availability for a counterfeit peace.

The Inner Presence. The spiritual error is mistaking withdrawal for transcendence. The tradition is clear that pratyāhāra is a practice of redirecting attention, not extinguishing it. The goal is not to stop perceiving but to perceive from a different center—from the stillness within, rather than from the reactive surface. When withdrawal becomes an end in itself, the person has not transcended the senses; they have merely abandoned them.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 11 AND c.slug = 'pratyahara';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When pratyāhāra is deficient, the person is a captive of their senses. Every notification demands attention. Every craving demands satisfaction. The mind is pulled in whatever direction the senses point, like a small boat towed by five different currents. The Gītā’s warning applies: “The senses are so impetuous that they forcibly carry away the mind even of a learned person who is endeavoring to control them” (II.60). And Manu’s observation: “If even one of the senses slips away, a person’s knowledge slips away through that sense, like water from a water-bag.”

The Somatic Base. The body in sensory captivity is in a state of perpetual overstimulation. The nervous system is frayed from constant input. There is a chronic inability to settle into stillness; the body fidgets, reaches for the phone, seeks the next source of stimulation. The attention economy of the twenty-first century is, in yogic terms, a civilization-scale experiment in pratyāhāra-deficiency.

The Emotional Current. The emotional life is reactive and volatile. Without the buffer that pratyāhāra provides, every sensory event triggers an emotional response, and every emotional response triggers a behavioral reaction. The person is, in the tradition’s language, “acting from the surface”—living in the outermost layer of their being, with no access to the deeper reservoirs of equanimity and discernment.

The Cognitive Map. The mind without pratyāhāra is what the tradition calls “all-pointed” (sarvārtha)—scattered in every direction, unable to sustain attention on a single object. This is not a failure of intelligence; it is a failure of containment. The mind may be brilliant but cannot bring that brilliance to bear on anything long enough to produce insight.

The Inner Presence. The soul in pratyāhāra-deficiency is like a lamp in a windstorm: the flame exists but cannot stabilize long enough to illuminate the room. The person may intuit that there is a deeper dimension of selfhood available, but they cannot access it because their attention is perpetually dissipated across the surface of sensory experience.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 11 AND c.slug = 'pratyahara';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When dhāraṇā is in equilibrium, the mind has achieved a capacity that is increasingly rare in the modern world: the ability to remain with a single object for an extended period. This is not the tense, effortful concentration of the student cramming for an exam; it is a relaxed, sustained attentiveness—the mind resting on its object the way a bird rests on a branch, alert but not straining.

The Somatic Base. The body in dhāraṇā-equilibrium is profoundly still but not rigid. The breath has slowed to a rate that would alarm a physician unfamiliar with meditative states. The metabolic rate drops. The pupils may dilate slightly, even with the eyes closed, as the visual cortex redirects its processing power to the internal object of attention. There is a warmth in the body that is not circulatory but energetic—the felt sense of prāṇa being channeled rather than dispersed.

The Emotional Current. The emotional tone is one of absorption: a quiet fascination with the object of concentration that is free of both desire and aversion. There is a particular flavor of pleasure that accompanies sustained concentration—what Mihāly Csíkszentmihālyi would later call “flow,” but what the yogic tradition identified millennia earlier as the sāttvic quality of the engaged mind. It is not the hedonic pleasure of sensory gratification but the eudaimonic pleasure of the mind functioning at its optimal capacity.

The Cognitive Map. The mind in dhāraṇā has narrowed its bandwidth to a single channel. Thoughts that are unrelated to the object of concentration still arise—Patañjali acknowledges this even in advanced practitioners (IV.27)—but they arise and pass without capturing attention, like birds crossing the periphery of an otherwise steady visual field. The person knows they are concentrating; there is still a distinction between the knower and the known. This distinction is what separates dhāraṇā from dhyāna.

The Inner Presence. Dhāraṇā teaches that consciousness has a natural power of coherence. Left undisturbed, the mind’s default is not chaos but order—not the forced order of discipline but the spontaneous order of a system that has been freed from the disturbances that fragmentize it. The practitioner begins to experience their own mind not as an obstacle to be overcome but as an instrument of extraordinary precision and beauty.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 11 AND c.slug = 'dharana';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When dhāraṇā tips into excess, concentration becomes fixation. The mind grips its object with a vise-like intensity that is not spacious but contracted. The person can sustain attention, but only at the cost of rigidity—a tension in the mental field that is the cognitive equivalent of a clenched fist. This produces a characteristic set of distortions: headaches, eye strain (even with closed eyes), a sense of exhaustion after practice rather than refreshment.

The Emotional Current. The excess of concentration produces a dry, joyless quality of attention. The sāttvic pleasure of genuine absorption is absent because the mind is not resting on its object but gripping it. There is a subtle aggression in the attentional stance: the mind is conquering the object rather than communing with it.

The Inner Presence. The spiritual error is mistaking willpower for wisdom. The ego has brought its familiar project of domination and control into the meditation chamber, and the object of concentration has become another territory to be conquered rather than a doorway to be entered.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 11 AND c.slug = 'dharana';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When dhāraṇā is deficient, the person simply cannot hold their mind in one place. They sit to meditate and are immediately swept into the current of associative thought. They begin a task and are distracted within minutes. This is not a character flaw; it is the natural consequence of insufficient preparation in the preceding limbs. Without ethical stability, the mind is noisy; without personal discipline, it is unstructured; without a prepared body, it is uncomfortable; without breath regulation, it is agitated; without sensory control, it is endlessly distracted.

The Inner Presence. The soul in dhāraṇā-deficiency is unable to see itself. Self-knowledge—the direct cognition of one’s own nature—requires a mind that can hold a mirror steady. The scattered mind is a shattered mirror: it catches fragments of light but cannot compose them into a coherent image. The person may have genuine longing for self-understanding, but without the capacity to sustain attention, that longing remains unfulfilled—the perpetual spiritual ache of the person who cannot sit still long enough to discover what they are.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 11 AND c.slug = 'dharana';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In dhyāna-equilibrium, the practitioner has crossed a threshold that changes the quality of consciousness itself. The mind is no longer working at meditation; meditation is happening. The distinction is experientially unmistakable and verbally almost impossible to convey. The closest analogy is the difference between swimming upstream and being carried by the current: the first is effortful, the second is a surrender to a larger movement.

The Somatic Base. The body in deep meditation is profoundly quiescent. The breath has become so subtle as to be almost imperceptible—a fact that Patañjali references in II.51, where he mentions a fourth type of prāṇāyāma that transcends the distinction between inhalation and exhalation. The musculature is completely relaxed, yet the spine remains erect—held not by muscular effort but by the upward movement of the subtle energies. The body temperature may drop. The metabolic signature resembles neither wakefulness nor sleep but occupies a unique physiological category that modern research has only begun to characterize.

The Emotional Current. The dominant emotional quality is a deep, sourceless bliss—what the tradition calls ānanda. This is not happiness in response to something; it is the intrinsic emotional tone of consciousness when it is no longer fragmented. There is a profound sense of coming home—not to a place but to a quality of being that feels more real, more fundamental, than ordinary waking experience.

The Cognitive Map. The most remarkable feature of dhyāna is the transformation of the relationship between awareness and its object. In ordinary cognition, there is a clear tripartite structure: the knower, the act of knowing, and the known. In dhyāna, this structure simplifies: the act of knowing and the known merge, and the knower remains only as a thin residual sense of witnessing. The image in the mind that has just passed is identical to the image that is present (III.12)—a sustained uniformity of cognition that is the experiential meaning of “one-pointedness.”

The Inner Presence. At the soul level, dhyāna is the penultimate step toward self-realization. The practitioner is now experiencing the mind in its purest sāttvic form—luminous, transparent, almost entirely free of the distortions of rajas and tamas. Vyāsa describes this state with a beautiful image: “Having reached the stage of intellectual luminosity, the wise person looks upon and compassionates others, as one upon a height looks down upon those in the plains.” The compassion is not condescension; it is the natural response of someone who has seen, from above the fog, how unnecessary most suffering is.

Vignette: The Hours That Aren’t

She sits at 4 AM, as she has for years. The meditation begins with dhāraṇā—the mind is fixed on the breath at the bridge of the nose—and for some minutes, there is the familiar dance of attention wandering and returning. And then, without a discernible transition, the dance stops. The breath is still there, but it is no longer an object she is observing; it is a current she is part of. The sense of sitting in a room falls away—not dramatically, but gently, the way the edges of things soften at dusk. There is awareness, and it is aware of itself, and there is a quality of silence that is not the absence of sound but the presence of something. When she opens her eyes, two hours have passed. She feels no stiffness, no grogginess. She feels, instead, as though she has been cleaned from the inside—as though every surface of her inner life has been wiped clear, and what remains is only light.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 11 AND c.slug = 'dhyana';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'To speak of samādhi in phenomenological terms is, paradoxically, to speak of the end of phenomenology—the dissolution of the very structures (subject, object, act of knowing) that make phenomenological description possible. Yet the tradition does provide descriptions, drawn from the testimony of practitioners who have returned from the state and attempted to render it in language.

The Somatic Base. In samādhi, the body is present but no longer experienced as a boundary. The practitioner does not leave the body; rather, the sense that the body is a container—a separate thing within which consciousness is housed—ceases. The body continues to function: the heart beats, the metabolism proceeds, the lungs draw air. But these processes are no longer experienced as “mine.” They are experienced, if at all, as impersonal events occurring within a field of awareness that is not localized.

The Emotional Current. The term ānanda—bliss—is traditionally associated with samādhi, but this is bliss unlike any emotional state ordinarily experienced. It is not the bliss of pleasure or the bliss of relief; it is the intrinsic radiance of consciousness itself, undistorted by the preferences and aversions that characterize ordinary emotion. The tradition describes seven stages of realization culminating in samādhi. Among the final stages: suffering has been completely identified, its causes completely eradicated, the mind has fulfilled its purpose and dissolved back into its matrix, and puruṣa shines forth in its own pure luminous nature.

The Cognitive Map. In samprajñāta-samādhi, cognition continues in a purified form. The mind knows its object with a directness and completeness that is qualitatively different from ordinary knowledge: Patañjali calls this ṛtambharā prajñā, “truth-bearing wisdom” (I.48)—a knowledge that is always and only of the essence of things. In asamprajñāta-samādhi, cognition itself ceases. There is no object, no act of knowing, no knower. There is only awareness—infinite, unqualified, self-luminous. This is the state that Patañjali identifies with the goal stated in the second sūtra of the entire text: citta-vṛtti-nirodhaḥ, the complete cessation of the fluctuations of the mind.

The Inner Presence. Samādhi is the resolution of the human condition as Patañjali understands it. The fundamental error—the confusion of puruṣa with prakṛti, of the self with the non-self, of the eternal with the temporal—is dissolved not through intellectual understanding but through direct experience. The soul recognizes itself. And in that recognition, the entire architecture of suffering—the kleśas, the karma, the saṁskāras, the endless cycle of birth and becoming—loses its power. Not because the world has changed, but because the one who was suffering has discovered that they were never the one who was suffering. They were always what they are now: pure consciousness, luminous and free.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 11 AND c.slug = 'samadhi';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Can there be an excess of samādhi? The tradition suggests there can, in a nuanced sense. The person who has tasted samādhi but has not fully integrated its implications may use the memory of the experience as an escape from the demands of embodied life. They may claim a realization they have not stabilized. They may dismiss the concerns of the body, of relationships, of ethical conduct as “illusory”—not from genuine realization but from a spiritual bypassing that uses the language of transcendence to avoid the work of living. Patañjali’s own structure guards against this: samādhi is the eighth limb, built upon the foundation of the other seven. A samādhi that is not grounded in ethical conduct, personal discipline, embodied awareness, and sensory mastery is not kaivalya; it is a peak experience that the ego has co-opted.

The tradition addresses this directly: “Yet even these [dhāraṇā, dhyāna, and samādhi] are external limbs in relation to seedless samādhi” (III.8). Even the highest experiences, as long as they contain any seed of individuality, any residual sense of “I am experiencing this,” are preliminary. The final samādhi is nirbīja—seedless—and in that state, there is no one left to claim the experience, no one left to misuse it. The excess, then, pertains only to the preliminary stages: the region where genuine glimpses are available but full stabilization has not yet occurred.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 11 AND c.slug = 'samadhi';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The deficiency of samādhi is, in Patañjali’s framework, the ordinary human condition. It is not a pathology; it is the starting point—the condition of a consciousness that has not yet recognized itself. The person in samādhi-deficiency identifies completely with the contents of the mind: with thoughts, emotions, memories, desires, and the body that houses them. They take the passing show for reality. They take the instrument of perception for the perceiver.

And yet, even in this state, the puruṣa is present. Awareness has not departed; it has merely been occluded, the way the sun is occluded by clouds. The person goes about their day, works, loves, suffers, laughs, grieves, and through all of it, awareness is silently witnessing—always present, always available, waiting only for the moment when the mind, exhausted by its own restlessness, finally grows still enough to notice what was there all along.

This is, perhaps, the most compassionate insight of the entire Yoga tradition: that the liberation being sought is not something to be achieved but something to be uncovered. The self is not becoming anything it is not already. It is simply remembering what it has always been.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 11 AND c.slug = 'samadhi';

-- -----------------------------------------------------------------------------
-- D12 — Architecture of Inner Life  (12 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (12, 'sanchita_karma', 'Sanchita Karma', NULL, 'Dimension I', 'Sanchita Karma represents the sum total of all past actions whose effects have not yet manifested—the entire library of books you have ever written, sitting on shelves in a room you cannot directly enter. It is the storehouse of all latent impressions, the deep subconscious programming that colors your fundamental inclinations.

Equilibrium

Somatic Base: The body feels like an instrument that has been well-played but carries no obvious tension from the playing. There is a neutral readiness in the musculature, a sense of being “settled into” the body without excess weight.

Emotional Current: A stable hum of quiet capability. You sense reserves of skill and intuition that seem to arrive without being summoned—what others call “natural talent.” There is no anxiety about these reserves; they simply exist, like groundwater.

Cognitive Map: Thoughts carry a quality of coherence. When faced with a new situation, the mind draws on a vast and varied library of past experience without becoming overwhelmed by it. Decisions feel informed rather than burdened.

Inner Presence: The witness recognizes that all current capacities are borrowed from a deep well—none are “personal achievements” in the egoic sense. There is gratitude without pride, capacity without inflation.

Excess: The Weight of Accumulated History

Somatic Base: A heaviness that cannot be attributed to any single cause—a sense of being “haunted” at the cellular level. The shoulders carry a load that no massage can release because the tension is not muscular but karmic.

Emotional Current: A pervasive undertow of “something unfinished.” The emotional landscape is tinged with a restless incompleteness, as though a debt exists that you cannot name. This may surface as chronic, low-grade anxiety or a sense of destiny that feels more like a cage than a calling.

Cognitive Map: Thought patterns spiral into fatalism. The mind tells stories of inevitability: “This is just who I am.” “I’ve always been this way.” The sheer volume of accumulated impression crowds out the possibility of genuine novelty.

Inner Presence: The spiritual lesson is one of purification through discernment. The witness sees the weight and recognises that not all of it must be carried forward. This is the territory where Jñāna Yoga—the path of discriminative knowledge—burns through layers of stored karmic residue.

Deficiency: The Rootless Feeling

Somatic Base: The body feels unmoored, as though it has arrived in this life without adequate “installation.” There is a lightness that is not freedom but disorientation—a lack of the embodied knowing that comes from having “been through” things.

Emotional Current: An inner emptiness that is not the spacious emptiness of meditative clarity but the thin emptiness of inexperience. The emotional range feels narrow, as though the instrument has few strings.

Cognitive Map: The mind struggles to find precedent. Each situation feels novel in a way that is disorienting rather than refreshing. Decision-making is slow and uncertain because there is little accumulated wisdom to draw upon.

Inner Presence: The soul’s lesson here is to engage fully with life rather than withdraw from it. The deficiency is an invitation to accumulate meaningful experience through the Path of Karma—not avoidance of action, but the wholehearted embrace of it.', 1),
    (12, 'prarabdha_karma', 'Prārabdha Karma', NULL, 'Dimension I', 'If Sanchita is the entire library, Prārabdha Karma is the specific chapter you are reading today. It is the portion of accumulated Karma that has “ripened” and is now actively playing out in the circumstances of your present life: the body you inhabit, the family you were born into, the era you live in, certain non-negotiable turning points that arrive regardless of current intention. The existentialists called this “Facticity”—the given terrain upon which all choice must be exercised.

Equilibrium

Somatic Base: The body is accepted as it is—its strengths, its limitations, its particular shape and rhythm. You wake with a chronic condition and manage it without resentment, treating the body as a “sacred constraint” rather than a punishment.

Emotional Current: A quality of philosophical acceptance permeates the emotional field. Difficult circumstances are met with a kind of dignified composure—not denial, but the recognition that resistance to the unchangeable consumes energy without producing change.

Cognitive Map: The mind focuses its analytical power not on “Why did this happen to me?” but on “Given that this is so, what is the wisest response?” This is the cognitive signature of high epistemic integrity in the face of Prārabdha.

Inner Presence: The witness understands that Prārabdha is not arbitrary but the precise curriculum needed for this particular soul’s growth. There is a deep, quiet trust in the intelligence of the process.

Excess: The Overwhelming Givens

Somatic Base: The body feels besieged by conditions it did not choose. Chronic pain, disability, or persistent illness dominate the somatic field, making every physical act a negotiation.

Emotional Current: A sense of cosmic injustice simmers beneath the surface. The emotional signature is a mix of helplessness and resentment—the feeling that the dice were loaded before you were ever born.

Cognitive Map: Victimhood narratives crystallize: “Life is fundamentally unfair.” “I never had a chance.” These stories are not entirely wrong—the facticity is genuinely heavy—but they foreclose the possibility of agency within constraint.

Inner Presence: The spiritual challenge here is immense: to find meaning within severe limitation. This is the territory of Bhakti—the path of devotion—where surrender to the larger intelligence becomes not resignation but a radical form of trust.

Deficiency: The Flight from Facticity

Somatic Base: The body is neglected because the person refuses to accept its current state. They may chase extreme interventions, jump between diets and surgeries, unable to sit with the body as it actually is.

Emotional Current: A persistent dissatisfaction with the “terrain” of one’s life. Rather than working the soil they have, the person fantasises about living in someone else’s field.

Cognitive Map: A cognitive pattern of perpetual comparison: “If only I had been born into that family, that country, that body.” The mind spends its energy on hypothetical alternatives rather than present possibilities.

Inner Presence: The soul’s lesson is that liberation is possible not despite constraints but through them. The prison becomes the monastery when the perspective shifts.', 2),
    (12, 'agami_karma', 'Āgami Karma', NULL, 'Dimension I', 'Āgami Karma (also called Kriyamāna) is the karma you are creating right now, in this breath, through the intentionality you bring to thought, word, and deed. If Sanchita is the entire library and Prārabdha is the chapter you are reading, Āgami is the sentence you are currently writing. This is the only arena where free will operates fully—the domain of genuine moral and spiritual agency.

Equilibrium

Somatic Base: The body acts with what the Yoga tradition calls “effortless effort.” Movements are purposeful without being tense. The hands do their work without gripping.

Emotional Current: There is engagement without obsession. You care about the outcome of your action but you are not chained to it. The Bhagavad Gītā’s instruction to “act without attachment to the fruit” is not philosophical abstraction here—it is the felt quality of a particular emotional stance.

Cognitive Map: The mind is focused on process rather than result. Thoughts are instruments of service rather than vehicles of self-promotion. There is clarity about why you are acting and what the action is meant to accomplish beyond personal gain.

Inner Presence: The witness performs action as an offering. This is Karma Yoga in its purest form: the action is fully engaged, but the actor has stepped aside. The residue left by such action is minimal because the seeds of attachment were not planted.

Excess: The Rajasic Overdrive

Somatic Base: The body is wired, over-caffeinated, perpetually “on.” Muscles remain partially engaged even during rest. The jaw clenches. Sleep is shallow and dream-filled with action sequences.

Emotional Current: A compulsive, driven quality infects every task. The emotional signature is obsession—not passion but its distortion. You cannot stop working, not because the work is meaningful, but because stopping would require you to feel what lies beneath the busyness.

Cognitive Map: Thought is dominated by planning, strategising, and outcome-tracking. The mind generates to-do lists inside to-do lists. Every conversation is evaluated for its utility toward the goal.

Inner Presence: The soul is being taught that there is a difference between right action and compulsive action. The lesson is that doing more does not always mean doing better, and that the quality of intention matters more than the quantity of output.

Deficiency: The Tāmasic Avoidance

Somatic Base: The body is sluggish, resistant to engagement. Getting out of bed requires an act of will that seems disproportionate to the task. There is a physical shrinking from the world—a desire to make oneself small and unnoticed.

Emotional Current: A flat, grey emotional tone. Not sadness exactly, but the absence of any motivating force—what the tradition calls ālasya (laziness) at the deepest level. Fear of failure has calcified into refusal to try.

Cognitive Map: The mind generates rationalisations for inaction: “It won’t matter anyway.” “Why bother when the outcome is uncertain?” These are not philosophical conclusions but the cognitive exhaust of Tāmasic inertia.

Inner Presence: The spiritual lesson is that inaction is itself a form of action—it creates its own Samskāra of withdrawal and contraction. The soul is being called to engage, even imperfectly, because engagement is the precondition for growth.', 3),
    (12, 'loka_vasana', 'Loka-vāsanā', NULL, 'Dimension III', 'This is the habitual orientation toward the external social world—the craving for validation, the dread of judgment, the compulsive calibration of self-worth against the opinions of others.

Equilibrium

Somatic Base: The body is at ease in social settings. Posture is open but not performative. Eye contact is natural rather than strategic. There is a physical relaxation that comes from not needing the room to approve of you.

Emotional Current: Social engagement carries a quality of genuine interest. You participate in community not because you need validation but because connection is inherently nourishing. The emotional tone is warmth without neediness.

Cognitive Map: The mind navigates social situations with a healthy awareness of social responsibility and etiquette. You respect community standards because they foster harmony, not because you are desperate for praise.

Inner Presence: The witness sees the social self as a useful interface, not a core identity. You can play social roles without becoming the mask.

Excess: The Performer

Somatic Base: The body is perpetually “on stage.” Posture is managed. Facial expressions are curated. After social events, there is a particular exhaustion that comes not from activity but from performance—the maintenance of a persona.

Emotional Current: The dominant transient states are Trāsa (anxiety about judgment), Asūyā (envy of those with higher status), and Mada (pride when recognition arrives). Self-worth oscillates violently between inflation and deflation based entirely on external feedback.

Cognitive Map: Every sentence in every conversation is pre-edited for impression management. The mind runs a constant background process: “How did that land? What do they think of me now? Did I say the right thing?” This consumes enormous cognitive bandwidth.

Inner Presence: The soul is being taught that the social self is a projection—a useful tool that has been mistaken for the master. The spiritual task is to discover who remains when the audience leaves.

Deficiency: The Hermit Without Purpose

Somatic Base: The body withdraws from social space. Physical presentation is neglected—not as an ascetic discipline, but as a symptom of disconnection.

Emotional Current: A cynical flatness replaces healthy social feeling. The person has not transcended the need for connection; they have merely armoured against the vulnerability it requires.

Cognitive Map: A self-reinforcing narrative of misanthropy: “People are not worth the effort.” “Society is a fraud.” These thoughts protect the ego from the risk of genuine engagement.

Inner Presence: The lesson here is that withdrawal from others, when driven by fear rather than genuine inner fullness, is just another form of bondage.', 4),
    (12, 'deha_vasana', 'Deha-vāsanā', NULL, 'Dimension III', 'This is the habitual identification with the physical body—its beauty, its comfort, its perceived flaws, its mortality. When Deha-vāsanā operates in balance, the body is treated as a “sacred instrument” with neutral respect. In excess, it becomes the entire horizon of identity.

Equilibrium

Somatic Base: The body is maintained as a fit vehicle for engagement—fed well, exercised, rested—without obsession. You notice physical sensations without being enslaved by them.

Emotional Current: There is a neutral affection for the body, like the feeling of a craftsman toward a well-maintained tool. Neither vanity nor neglect.

Cognitive Map: Thoughts about the body are practical and proportionate. You do not spend the morning in front of the mirror, nor do you ignore the body’s signals.

Inner Presence: The witness recognises the body as a temporary dwelling—precious but impermanent. There is care without clinging.

Excess: The Imprisoned Self

Somatic Base: Every physical sensation is amplified. A minor blemish, a new wrinkle, a slight pain becomes an emotional crisis. The body is no longer an instrument but a cage whose walls are inspected obsessively.

Emotional Current: The dominant transient states are Mada (vanity) and Glāni (a heavy, draining exhaustion tied to bodily anxiety). Every ageing sign is met with terror; every physical compliment is hoarded as proof of worth.

Cognitive Map: Thought is dominated by the body’s appearance and condition. Hours are spent on grooming routines, health forums, or hypochondriac research. The mind cannot think about anything else because the body has absorbed the entire identity.

Inner Presence: The soul is being confronted with a fundamental question: “Am I this body, or am I the awareness that inhabits it?” The excess is the teacher, pushing the identification to its breaking point.

Deficiency: The Abandoned Vehicle

Somatic Base: The body is neglected—under-fed or poorly nourished, under-rested, unexercised. Physical signals of distress are ignored or suppressed.

Emotional Current: A flat indifference toward physical wellbeing. This is not the serene detachment of the sage but the nihilistic dismissal of the body as “just matter.”

Cognitive Map: The mind rationalises neglect through pseudo-spiritual reasoning: “The body is an illusion anyway.” This is intellectual laziness disguised as transcendence.

Inner Presence: The lesson is that the body, as the Annamaya Kośa, is the necessary foundation for all higher work. Ignoring it does not transcend it; it merely ensures that its unmet needs will sabotage every other layer.', 5),
    (12, 'sastra_vasana', 'Śāstra-vāsanā', NULL, 'Dimension III', 'This is the paradoxical tendency: even the pursuit of wisdom can become a cage. Śāstra-vāsanā is the habitual collection of knowledge without embodiment—the accumulation of scriptural fact, philosophical argument, and conceptual framework as a substitute for actual transformation.

Equilibrium

Somatic Base: Study is balanced with practice. The body is used as a laboratory for the theories the mind has absorbed. You read about Prāṇāyāma and then practice it; you study the Guṇas and then observe them in your own behaviour.

Emotional Current: Knowledge brings a quiet joy—the satisfaction of understanding aligned with the humility of knowing how much remains unknown.

Cognitive Map: The mind uses scriptures as a map, not a destination. Knowledge refines conduct and deepens perception. You do not study to win arguments; you study to see more clearly.

Inner Presence: The witness holds knowledge lightly, knowing that the finger pointing at the moon is not the moon.

Excess: The Intellectual Hoarder

Somatic Base: The body atrophies. Hours are spent in sedentary study. The physical world recedes as the mind builds elaborate conceptual structures that have no foundation in embodied experience.

Emotional Current: The dominant transient states are Mada (intellectual pride), Garva (haughtiness), and Amarsha (impatience with those who know less). Debate becomes blood sport.

Cognitive Map: The mind is a fortress of definitions, citations, and arguments. Every conversation is an opportunity to display knowledge. The irony is devastating: the person has read every text about ego-dissolution but their ego has never been larger.

Inner Presence: The soul is learning that information is not realisation, that knowing about fire is not the same as being warm.

Deficiency: The Unexamined Life

Somatic Base: The body moves through life on autopilot. Without the intellectual framework to recognise patterns, physical habits are never questioned.

Emotional Current: A vague sense that “something is off” but no vocabulary to name it. Emotional states wash through without being understood or integrated.

Cognitive Map: The mind lacks the conceptual tools for self-reflection. Life is lived reactively, governed by impulse and circumstance rather than by discernment.

Inner Presence: The soul is calling for engagement with the question “Why?”—the beginning of the Path of Jñāna.', 6),
    (12, 'kama_vasana', 'Kāma Vāsanā', NULL, 'Dimension III', 'This is the general tendency toward sensory gratification—the pull toward taste, touch, sight, sound, and smell as primary sources of fulfilment. Kāma Vāsanā is not inherently destructive; the capacity for sensory delight is part of the human endowment. Its danger lies in its capacity to become the sole organising principle of a life, eclipsing the subtler forms of satisfaction available through the higher Kośas.

When Kāma Vāsanā is dominant, it generates a characteristic set of transient states: Autsukya (longing/impatience), Capalata (restlessness/fickleness), Glāni (the “crash” after sensory over-indulgence), and Nirveda (the flash of regret when the pleasure proves temporary). The lived experience is a cycle of anticipation, consumption, depletion, and renewed craving—the hedonic treadmill rendered in Sanskrit.', 7),
    (12, 'subha_vasana', 'Subha Vāsanā', NULL, 'Dimension III', 'The Subha Vāsanā is the tendency toward truth, service, meditation, and inner stillness. It generates transient states that are “expansive” rather than “contractive”: Dhṛti (fortitude/contentment), Harsha (selfless joy), Mati (clear determination), and Smṛti (mindfulness—the sudden, grounding wave of remembering one’s true nature in the middle of a chaotic moment). In a stressful meeting, you feel the impulse to snap at a colleague; then a Subha Vāsanā triggers a moment of Smṛti. You remember your commitment to epistemic integrity. The anger dissolves, replaced by Dhṛti. No new binding Karma is created. The old groove softens.', 8),
    (12, 'lokesana', 'Lokeśana', NULL, 'Dimension IV', 'The drive for social recognition, public esteem, and the “good opinion” of the world. Lokeśana is the primary engine behind Loka-vāsanā, and when it is dominant, it tethers identity to external validation with a ferocity that can eclipse every other concern.

Equilibrium

Somatic Base: The body is relaxed in public spaces. There is no compulsive self-monitoring—no checking of reflection in shop windows, no adjusting of posture when a perceived authority enters the room.

Emotional Current: A quiet sense of purpose that does not require external affirmation. You contribute your best work because the work itself demands it, not because the audience is watching.

Cognitive Map: The mind evaluates feedback on its merits. Criticism does not destabilise; praise does not inflate. There is a steady internal compass that social weather cannot permanently alter.

Inner Presence: The witness understands that reputation is a shadow cast by action—useful but ultimately insubstantial. Identity rests in the witness, not in the reflection.

Excess: The Prisoner of the Gaze

Somatic Base: Chronic tension in the face and throat—the muscles of “presentation.” The body is perpetually braced for evaluation. Heart rate spikes at the ping of a notification.

Emotional Current: A volatile emotional economy where self-worth is denominated in likes, titles, and invitations. The transient states are Trāsa (fear of being “cancelled”), Asūyā (envy of those with higher visibility), and the particular agony of Autsukya (impatient longing for the next validation hit).

Cognitive Map: Every action is pre-filtered through the question: “How will this look?” Authenticity is sacrificed at the altar of optics. The person tailors every sentence to sound impressive rather than true.

Inner Presence: The soul is trapped behind a mask it has mistaken for its own face. The spiritual lesson is that the social self is a projection; the real self persists even when the audience leaves.

Deficiency

Somatic Base: A withdrawal from public space. The body retreats into smallness—hunched shoulders, averted gaze, minimal physical presence.

Emotional Current: Not humility but shame. Not transcendence of status but terror of judgment. The person avoids visibility not because they have outgrown the need for it, but because they cannot bear the risk of receiving negative feedback.

Cognitive Map: A narrative of unworthiness: “I have nothing to contribute.” “No one wants to hear from me.” These thoughts are not realistic self-assessment but the cognitive signature of a Lokeśana that has collapsed inward.

Inner Presence: The spiritual invitation is to reconnect with the intrinsic worth of contributing to the world—not for the sake of recognition, but because service is the natural expression of an awakened being.', 9),
    (12, 'vittesana', 'Vitteśana', NULL, 'Dimension IV', 'The drive for financial security, material accumulation, and the comfort that resources provide. At its core, Vitteśana is the belief that safety can be purchased, that enough material padding can insulate the self from the fundamental uncertainty of existence.

Equilibrium

Somatic Base: The body is comfortable with enough. There is no hoarding impulse in the muscles, no clenched fist around possessions. Material resources are managed with the steady hand of a custodian rather than the tight grip of an owner.

Emotional Current: Financial matters are handled with equanimity. A downturn in the market does not produce existential terror; a windfall does not produce euphoria. Wealth is a tool, and tools do not define their wielder.

Cognitive Map: The mind understands the difference between sufficiency and excess. Financial planning is pragmatic rather than obsessive. Generosity flows naturally because there is no core belief in scarcity.

Inner Presence: The witness sees wealth as a trust to be managed for the benefit of the Whole, not a fortress to be defended.

Excess: The Bottomless Pit

Somatic Base: A physical tightness in the chest and stomach—the somatic signature of “not enough.” The body is in a permanent state of low-grade acquisition mode. Shopping, checking investment portfolios, counting—these activities produce a brief somatic release followed by a deeper contraction.

Emotional Current: The dominant transient states are Lobha (greed—a tightening hunger that no amount of accumulation satisfies), Trāsa (anxiety about losing what has been gained), and the relentless Autsukya (impatient longing for the next acquisition). Financial loss is experienced not as a practical setback but as an assault on identity.

Cognitive Map: The mind reduces all relationships and opportunities to their financial dimension. People are evaluated for their economic utility. The internal monologue is dominated by calculations, projections, and scenarios of loss.

Inner Presence: The soul is learning that material security, pursued to its limit, reveals itself as a mirage—each destination recedes as you approach it.

Deficiency

Somatic Base: Chronic insecurity manifesting as physical anxiety—sleepless nights, digestive disturbance, the body braced for deprivation.

Emotional Current: A pervasive sense of scarcity that has calcified into identity. Even in objective abundance, the person feels poor. Generosity feels dangerous because every gift is experienced as a diminishment.

Cognitive Map: Scarcity thinking dominates: “There is never enough.” “I cannot afford to be generous.” These thoughts have become background radiation, colouring every decision.

Inner Presence: The spiritual invitation is to discover the inner abundance that does not depend on external resources—the wealth of awareness itself.', 10),
    (12, 'putresana', 'Putreśana', NULL, 'Dimension IV', 'The desire for biological or creative continuity—for one’s name, bloodline, ideas, or creations to persist beyond the boundary of personal death. Putreśana is a subtle extension of Deha-vāsanā (bodily identification), projected forward in time. It is the ego’s attempt to achieve a kind of immortality by extending itself into other beings or enduring works.

Equilibrium

Somatic Base: The body is at peace with its temporality. You hold a child, mentor a student, or tend a creative project with full presence, knowing that the act of nurturing is complete in itself, regardless of what endures.

Emotional Current: There is joy in contributing to the next generation or the next iteration without needing it to bear your name. The emotional quality is one of open-handed giving.

Cognitive Map: The mind sees the difference between contributing to the river and damming the river. You understand that true legacy is not in what bears your signature but in the quality of consciousness you transmit.

Inner Presence: The witness knows that continuity at the deepest level is not of the body or the name but of the Dharma—the universal order that persists beyond any individual expression.

Excess: The Puppet Master

Somatic Base: A clutching energy in the hands and arms—the physical signature of someone who cannot let go. Shoulders are raised as though bracing against the current of time.

Emotional Current: Asūyā (envy of other families’ or successors’ achievements), Mohā (delusion regarding the importance of one’s family name), and Amarsha (impatience when a student or child challenges your “wisdom”). The successor becomes a canvas for the ego’s unfinished self-portrait.

Cognitive Map: A narrative of ownership: “They are my legacy. They must do things my way.” The mind confuses guidance with control, love with possession.

Inner Presence: The soul is being asked: “Are you loving this person, or are you loving your own reflection in them?”

Deficiency

Somatic Base: A physical sense of futility—the shoulders slump, the eyes lose their forward orientation. The body communicates that there is nothing ahead worth investing in.

Emotional Current: A nihilistic indifference to the future. Not the wise acceptance of impermanence, but the despairing conclusion that nothing matters because nothing lasts.

Cognitive Map: The mind generates variations of “What is the point?” without the energy to answer the question.

Inner Presence: The soul is being invited to discover that meaning does not require permanence—that the act of giving, in the moment of giving, is already complete.', 11),
    (12, 'jivesana', 'Jīveśana', NULL, 'Dimension IV', 'The most primal of the four Eśanas. Jīveśana is the deep-seated “will to live,” the instinctive recoil from anything that threatens the continuity of the ego-identity. Patanjali calls its subtlest form Abhiniveśa—the clinging to life that persists even in the wise. It is the root of all bodily identification and the engine of fear at the most fundamental level.

Equilibrium

Somatic Base: The body’s survival instincts are intact and functional without being hyper-activated. You wear a seatbelt without obsessing about car accidents. You eat healthily without treating every meal as a battle against death.

Emotional Current: There is a healthy respect for life and its fragility, combined with a willingness to engage with risk when the situation demands it. Fear is present but proportionate.

Cognitive Map: The mind acknowledges mortality without being paralysed by it. There is a philosophical ease with the fact of impermanence that allows full engagement with the present.

Inner Presence: The witness holds the body’s survival drive with compassion but does not confuse the drive with identity. The deepest question—“Who dies?”—has been sincerely engaged.

Excess: The Fortress Builder

Somatic Base: The nervous system is perpetually in a low-grade fight-or-flight state. The body reads every change—a new symptom, a corporate restructuring, a shift in a relationship—as a mortal threat. Chronic hyper-vigilance depletes the adrenal system.

Emotional Current: Trāsa (terror) is the dominant note—not the acute terror of a crisis, but the chronic, slow-burning dread that colours every day. Dainya (helplessness) descends when the dread becomes overwhelming, and Mohā (delusion) manifests as a frantic attempt to cling to the past, refusing to accept the reality of change.

Cognitive Map: The mind is consumed by risk assessment and catastrophic projection. Every health article is a prophecy. Every news headline is a harbinger. The cognitive style is anticipatory grief—mourning losses that have not yet occurred.

Inner Presence: The soul is being presented with its most fundamental examination: “Am I the body that will die, or am I the awareness that observes the body’s changes?” This Eśana, more than any other, forces the ultimate philosophical question.

Deficiency

Somatic Base: A reckless disregard for physical safety. The body is thrown into dangerous situations not out of courage but out of a nihilistic disconnection from its own value.

Emotional Current: A flat emotional relationship to one’s own continuation. Not the serene acceptance of the sage, but the exhausted indifference of someone who has stopped caring.

Cognitive Map: A cognitive pattern that minimises the value of embodied life: “It doesn’t matter.” “Nothing lasts anyway.” These thoughts are not wisdom but the Tāmasic collapse of the survival instinct.

Inner Presence: The spiritual correction is a renewed appreciation for the preciousness of embodied life—not because the body is permanent, but because it is the vehicle through which the soul can do its work.

PART TWO

The Interlocking System in Motion', 12);

-- -----------------------------------------------------------------------------
-- D13 — Cyclical Evolution of Consciousness  (3 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (13, 'the_descending_arc', 'The Descending Arc', NULL, 'Pravṛtti Mārga', NULL, 1),
    (13, 'the_nadir', 'The Nadir', NULL, 'The Turning Point', NULL, 2),
    (13, 'the_ascending_arc', 'The Ascending Arc', NULL, 'Nivṛtti Mārga', NULL, 3);

-- D13 pole descriptions (9 rows)
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Somatic Base (Physical)

The body feels vital and forward-leaning. There is a warmth in the chest, a readiness in the limbs. Appetite is healthy and directed toward dense, nourishing foods—grains, proteins, earthy flavours. Sleep is deep and restorative, serving the body’s need to process the day’s acquisitions. The senses are sharp and attuned to the external environment: colours are vivid, sounds carry information, touch connects the self to the world’s textures. The body feels like a well-tuned instrument for engaging with material reality.

Emotional Current (Vital)

The dominant emotional tone is engaged enthusiasm. There is a healthy ambition—not the frantic grasping of excess but a genuine delight in building, creating, and participating in the world. The Eśanas (cravings for wealth, progeny, fame, and self-preservation) are present but proportionate: the desire to provide for one’s family, to be recognised for good work, to build something lasting, to protect one’s health. These drives feel natural, not pathological. The emotional body hums with a creative tension that makes projects feel exciting and relationships feel substantial.

Cognitive Map (Mental)

The mind operates in a predominantly pragmatic-analytical mode. Thoughts cluster around planning, strategy, and the navigation of worldly challenges. The question “How can I make this work?” dominates the cognitive landscape. There is relatively little interest in abstract philosophical questions—not from incapacity, but because the soul’s current lesson is engagement with form. The mind is solution-oriented, pattern-recognising, and efficient. Time is experienced as a resource to be managed.

Inner Presence (Psychic)

At the soul level, the descending arc in equilibrium is the curriculum of individuation. The soul is learning what it means to be a particular self in a particular body in a particular time—the full weight and wonder of embodied existence. The spiritual lesson is not rejection of the world but thorough participation in it. The jīva is gathering the experiential data that will eventually—across many lifetimes—create the conditions for the inward turn. There is a hidden grace in the descent: every deep engagement with form is, paradoxically, training the consciousness to eventually see through form.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 13 AND c.slug = 'the_descending_arc';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the descending orientation becomes excessive, the soul loses the natural balance between engagement and awareness. The world is no longer a place of learning but a place of conquest. Identity becomes entirely fused with external markers—title, net worth, appearance, legacy—and the interior life is colonised by the logic of accumulation.

Somatic Base (Physical)

The body becomes a status vehicle. It is either obsessively maintained (gym rituals, appearance management, anti-ageing regimens driven by Jiveśana) or neglected in service of work (the executive who hasn’t exercised in years because “there’s no time”). The nervous system is chronically activated: cortisol hums constantly, jaw clenches during sleep, the stomach processes stress rather than food. The body feels like a machine to be optimised, not a home to be inhabited.

Emotional Current (Vital)

The Eśanas become dominant and distorted. Vitteśana (craving for wealth) metastasises from healthy provision into compulsive accumulation. Lokeśana (craving for fame) transforms from healthy pride in good work into addiction to external validation. Putreśana (craving for legacy) turns children or creative projects into extensions of ego rather than expressions of love. The emotional baseline is anxious striving—a constant, low-grade fear that one has not yet acquired enough to be safe.

Cognitive Map (Mental)

The mind becomes a calculation engine. Every interaction is evaluated for strategic value. Relationships are scored on their utility. The inner monologue sounds like a perpetual cost-benefit analysis: “What does this person offer me? What’s the ROI on this friendship? How does this event advance my position?” The cognitive map narrows to a single axis: win/lose. Nuance, beauty, and non-instrumental value are filtered out as irrelevant.

Inner Presence (Psychic)

The soul-level lesson in excess descent is the exhaustion of the outward path. The jīva is being shown, through the very completeness of its material engagement, that no external achievement can provide the peace it seeks. Every acquisition reveals a new absence; every summit reveals a higher peak. The karmic consequence is an accelerating accumulation of saṃskāras that will require significant clearing during the eventual ascending phase. The excess is not wasted—it is data the soul is collecting about the limits of form.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 13 AND c.slug = 'the_descending_arc';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficiency in the descending arc manifests when a soul that is positioned for worldly engagement refuses the engagement. This is not the genuine vairāgya (dispassion) of the ascending soul; it is a premature withdrawal—a spiritual bypassing that uses the language of transcendence to avoid the messy work of embodied living.

Somatic Base (Physical)

The body feels thin and ungrounded. There is a quality of not-quite-being-here: the person seems to hover slightly above their own life. Appetite is poor or erratic—food is treated as either an inconvenience or a guilty pleasure rather than a natural part of embodied existence. The immune system may be compromised from the stress of fighting one’s own nature. There is a characteristic energetic flatness—the vital force that should be flowing outward into the world is being artificially dammed.

Emotional Current (Vital)

The emotional tone is a peculiar spiritual superiority combined with underground resentment. The person presents as “above” worldly concerns but harbours suppressed envy toward those who engage fully with life. The Eśanas are still present (they must be, given the soul’s evolutionary position) but are disowned and driven underground, where they express as passive-aggressive behaviour, martyrdom, or covert materialism disguised as spiritual detachment.

Cognitive Map (Mental)

The mind constructs elaborate justification narratives for the withdrawal. “I’m too evolved for corporate life.” “Money is dirty.” “Relationships are attachments.” These beliefs sound spiritual but function as defense mechanisms, protecting the ego from the vulnerability of genuine engagement. The cognitive map is dominated by dualistic thinking: spiritual vs. material, pure vs. corrupt, evolved vs. primitive—categories that the ascending soul eventually transcends but that the descending soul uses to avoid its own curriculum.

Inner Presence (Psychic)

The soul-level lesson in deficient descent is the honesty of engagement. The jīva is being invited to recognise that its current evolutionary task is not transcendence but incarnation—full, honest, messy participation in the world of form. The spiritual bypass creates a kind of karmic stalling: no new saṃskāras of genuine experience are being created, but neither are the conditions for eventual ascent being properly laid. The soul is, in effect, refusing its own curriculum—and the curriculum will simply present itself again, often with greater insistence, in the next lifetime.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 13 AND c.slug = 'the_descending_arc';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Somatic Base (Physical)

The body at the nadir in equilibrium feels heavy but honest. There is a tiredness that is not merely physical but existential—a bone-deep fatigue that no amount of sleep fully resolves. The body has begun to communicate in symptoms: chronic tension in the shoulders (carrying the accumulated weight of saṃskāras), digestive disturbances (the system struggling to process what has been consumed), a general sense of physical density. Yet there is also a new quality: a certain stillness that was not present during the active descent. The body is slowing down, and in its slowness, it becomes available for a different kind of listening.

Emotional Current (Vital)

The dominant emotional signature is nirveda—a deep, pervasive world-weariness that the tradition distinguishes from depression (though the two can overlap). Nirveda is specifically the emotional state that arises when the soul has genuinely exhausted its fascination with what the world offers. It is not the bitterness of the disappointed materialist but the quiet sorrow of one who has tasted everything and found it insufficient. There is a quality of mourning in this state—a grieving for the innocence of uncritical engagement that will not return.

Cognitive Map (Mental)

The mind begins asking questions it has never asked before—or has avoided asking. “Is this all there is?” is the signature nadir question, but beneath it lie more specific inquiries: “Why does getting what I want never feel like enough?” “Who am I when I’m not performing?” “What would it mean to live from something other than ambition?” The cognitive map is in a state of productive disorientation—the old categories (success/failure, winning/losing) no longer organise experience effectively, but no new framework has yet replaced them.

Inner Presence (Psychic)

The soul at the nadir in equilibrium is at the threshold of the most significant transition in its evolutionary cycle. The jīva is being prepared for the inward turn—not through instruction but through the visceral experience of the outer path’s limitations. The spiritual lesson is surrender—not in the sense of defeat, but in the sense of releasing the grip on what has been and opening to what might be. This is the moment when, as the tradition puts it, the soul begins to recognise that “every decay is merely preparation for a new beginning.”', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 13 AND c.slug = 'the_nadir';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the nadir state becomes excessive, the soul reaches the turning point but refuses to turn. Instead of allowing the crisis to catalyse transformation, the individual doubles down on the very strategies that created the crisis, pushing deeper into material accumulation, sensory stimulation, or ego-reinforcement in an increasingly desperate attempt to silence the inner signal of insufficiency.

Somatic Base (Physical)

The body enters a state of aggressive compensation. The person may pursue extreme fitness regimens, cosmetic procedures, or stimulant use to override the body’s natural signal of slowing down. Or they may collapse into complete somatic neglect—the body becoming a burden they drag through their schedules. Addictive patterns often emerge at this stage: the nervous system, denied the profound rest that the turning point demands, seeks artificial regulation through alcohol, work addiction, or compulsive consumption. The body’s attempts to communicate are systematically overridden.

Emotional Current (Vital)

The nirveda (world-weariness) that characterises the equilibrium nadir is suppressed and replaced with artificial intensity. The person manufactures drama, crisis, or conflict to avoid the quiet despair beneath. Relationships become either sources of distraction or targets of blame. The Eśanas are now operating in panic mode: Vitteśana manifests as hoarding; Lokeśana as desperate reputation management; Jiveśana as existential terror masked as anger. The emotional signature is brittleness—a hardened surface over a terrified core.

Cognitive Map (Mental)

The mind becomes a defense lawyer for the status quo. The questions that arose naturally at the equilibrium nadir (“Is this all there is?”) are reframed as weakness: “That’s just a midlife crisis. Everyone goes through it. Stay the course.” The cognitive map rigidifies around familiar narratives of success, control, and self-sufficiency. Any information that threatens these narratives—a health diagnosis, a child’s honest feedback, a quiet moment of self-recognition—is either rationalised away or converted into a problem to be “solved” with more of the same strategies.

Inner Presence (Psychic)

The soul-level consequence of refusing the nadir’s invitation is karmic deepening. Each refusal to acknowledge the crisis generates a new layer of binding saṃskāras—impressions of denial that will require additional lifetimes to resolve. The jīva is, in effect, extending its time at the bottom of the cycle. The tradition does not frame this as punishment but as consequence: the turning point will keep presenting itself, with increasing urgency, until it is finally honoured.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 13 AND c.slug = 'the_nadir';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficiency at the nadir manifests when the individual recognises the crisis but short-circuits the process by claiming a spiritual transformation that has not actually occurred. This is the nadir’s version of spiritual bypassing: the person adopts the language and postures of the ascending arc without having genuinely undergone the inner dissolution that the nadir demands.

Somatic Base (Physical)

The body displays performative lightness. The person may adopt austere dietary practices, demonstrate conspicuous flexibility or stillness, or affect the calm physical demeanour associated with spiritual advancement. But the body’s deep patterns have not changed: the same tension lives in the jaw, the same cortisol signature marks the sleep cycle, the same flinch responses operate in moments of genuine challenge. The somatic base knows the transformation is cosmetic, even when the conscious mind insists otherwise.

Emotional Current (Vital)

The emotional signature is spiritual enthusiasm overlying unprocessed grief. The person may display intense devotional emotion, dramatic claims of insight, or a conspicuous serenity that crumbles under pressure. The nirveda (world-weariness) that is the genuine emotional content of the nadir has been papered over with a adopted emotional repertoire—the vocabulary of “surrender” and “acceptance” deployed before the actual experience of either has occurred.

Cognitive Map (Mental)

The mind constructs an identity of spiritual arrival. “I’ve had my crisis. I’ve done the work. I’m on the other side.” This narrative is maintained by selective interpretation of experience: moments of peace are taken as evidence of transformation; moments of struggle are dismissed as “residual patterns” that will “work themselves out.” The cognitive map is paradoxically similar to the excess nadir’s rigidity—both refuse the uncertainty of genuine transition.

Inner Presence (Psychic)

The soul-level lesson in deficient nadir is the patience of genuine transformation. The jīva is being shown that the turning point is not a moment but a process—one that cannot be accelerated through will alone. The premature claim of ascent creates a particularly subtle form of saṃskāra: the impression of being “beyond” the crisis, which paradoxically anchors the soul more firmly at the nadir by preventing the honest reckoning that the genuine turn requires.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 13 AND c.slug = 'the_nadir';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Somatic Base (Physical)

The body in balanced ascent feels lighter but more present. There is a quality of settled alertness—the system is neither hyper-activated nor collapsed. Appetite becomes naturally moderate; the person gravitates toward simpler foods without needing to impose dietary rules. Sleep is deep but requires less time—the consciousness is beginning to need less escape from itself. The senses are still fully functional but their grip has loosened: a beautiful sunset is appreciated without the urgency to possess it; a sharp noise is registered without the full cascade of stress response. The body becomes, increasingly, a transparent instrument rather than a dense identity-anchor.

Emotional Current (Vital)

The emotional baseline shifts from desire-driven engagement to appreciative equanimity. The Eśanas are still present but progressively less compelling: wealth matters less than sufficiency, recognition less than integrity, legacy less than presence. The dominant emotional tone is dhṛti (fortitude/contentment)—a steady, warm stability that does not depend on external circumstances. Joy arises more frequently, not because life is better but because the filter of craving has thinned and reality is perceived more directly. There is also, importantly, a quality of karuṇā (compassion) that emerges naturally: having navigated one’s own descent and nadir, the ascending soul recognises the same patterns in others without judgment.

Cognitive Map (Mental)

The mind becomes discerning rather than calculating. The pragmatic intelligence of the descent is not lost but is supplemented by a growing capacity for viveka (discrimination between the real and the unreal). The question “How do I get what I want?” gives way to “What is actually happening?” and eventually to “Who is the one watching all of this?” Thought becomes less compulsive; the space between thoughts widens. The mind is still a useful tool but is no longer the master of the house.

Inner Presence (Psychic)

The soul in balanced ascent is engaged in the curriculum of liberation. Each cleared saṃskāra represents a small increment of freedom—not freedom from experience but freedom within it. The jīva is learning to be the Witness (Sākṣī) rather than the actor—to observe the play of life without being compelled to identify with any particular role. The tradition describes this as the consciousness gradually recognising that it is not the changing body, emotions, or thoughts but the unchanging awareness in which all of these arise. This recognition deepens with each cycle of practice, and the tradition teaches that those who have done enough practice in previous births will feel “different energies, different śaktis in different chakras,” even in waking states.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 13 AND c.slug = 'the_ascending_arc';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Excess in the ascending arc manifests as spiritual perfectionism—the soul that has genuinely begun the inward journey but becomes rigidly attached to the identity of being on the path. The ascent itself becomes a new object of ego-identification, and the very tools of liberation (practice, renunciation, knowledge) become subtle chains.

Somatic Base (Physical)

The body is subjected to ascetic overreach. The person may fast excessively, maintain punishing meditation schedules, or deny the body’s legitimate needs (rest, warmth, pleasure) in the name of spiritual progress. The body’s natural vitality—which is itself a gift of prāṇa and necessary for sustained practice—is depleted by the very practices meant to refine it. The somatic signature is taut and brittle: the person looks disciplined but feels fragile.

Emotional Current (Vital)

The emotional tone becomes dry and judgmental. The genuine compassion of balanced ascent is replaced by a subtle spiritual superiority: other people’s struggles are viewed as evidence of their inferior evolutionary position rather than as invitations for empathy. The person may develop an allergy to emotional expression—their own or others’—interpreting all emotion as “attachment” to be eliminated. The vairāgya (dispassion) has hardened into emotional avoidance, and the dhṛti (fortitude) has become rigidity.

Cognitive Map (Mental)

The mind becomes a spiritual scorecard. Progress is meticulously tracked: hours of meditation, stages of samadhi achieved, texts mastered, visions experienced. The cognitive map is organised around a hierarchy of spiritual attainment, with the self carefully positioned above most others. The tradition’s teachings are used not as mirrors for self-examination but as weapons for self-aggrandisement. The fundamental question of the ascending arc—“Who is the Witness?”—has been replaced by “How far have I progressed?”

Inner Presence (Psychic)

The soul-level lesson in excess ascent is the final surrender of the spiritual ego. The tradition teaches that even sattva (purity/harmony), when clung to, becomes a golden chain. The Bhagavad Gītā describes this: those dominated by psychic energy will do good work, give charity, read scriptures, and perform sādhanā—“but all these are due to sattva.” A state comes when the person must go beyond even sattva—when there is no longer any urge even to practise because “the traveller and the goal have merged in one.” Excess ascent is the last obstacle before this final dissolution of the separate practitioner.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 13 AND c.slug = 'the_ascending_arc';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficiency in the ascending arc describes the soul that has genuinely begun the inward turn but loses momentum. The tradition describes this with precision: “If one is doing meditation regularly, every day the system is being charged. But if there is a break in sādhanā, it is just one step forward, two steps backward.”

Somatic Base (Physical)

The body reflects the inconsistency of practice. There are periods of clarity—when the person is meditating regularly, the body feels light and settled—followed by periods of collapse when practice lapses and the old heaviness returns. The somatic experience is one of oscillation: the person knows what a regulated nervous system feels like but cannot sustain it. This oscillation creates its own form of suffering—worse, in some ways, than the consistent density of the nadir, because the person has tasted freedom and keeps losing it.

Emotional Current (Vital)

The emotional signature is intermittent aspiration undercut by recurring habit. During periods of practice, the person experiences genuine dhṛti and harṣa (joy). During lapses, old saṃskāras reassert themselves: the familiar patterns of craving (Eśanas), restlessness (capalatā), and self-disparagement (nirveda) return. The emotional landscape becomes a battlefield between the ascending momentum and the gravitational pull of uncleared impressions.

Cognitive Map (Mental)

The mind splits between aspiration and self-recrimination. The person knows what they “should” be doing (practising, studying, serving) and knows they are not doing it consistently. This gap between intention and action generates a cognitive loop of guilt, resolution, brief effort, and relapse. The mind may develop a defeatist narrative: “Maybe I’m not cut out for this path.” This narrative, left unchallenged, can stall the ascent for extended periods.

Inner Presence (Psychic)

The soul-level lesson in stalled ascent is the virtue of patient persistence. The tradition is clear that progress on the ascending arc is cumulative: what was accomplished in previous births carries forward, and even halting, inconsistent effort is not lost. The jīva is being invited to develop śraddhā (faith)—not blind belief but experiential trust based on what it has already glimpsed. The stalled ascent is not failure; it is the normal rhythm of a consciousness learning to sustain an orientation that is fundamentally counter to the momentum of countless descending lifetimes.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 13 AND c.slug = 'the_ascending_arc';

-- -----------------------------------------------------------------------------
-- D14 — Yuga Cycles  (4 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (14, 'satya_yuga', 'Satya Yuga', NULL, 'The Age of Truth-Consciousness', 'In Satya Yuga, the field of collective consciousness operates at its highest capacity. Dharma is not a principle to be followed but the very atmosphere in which life unfolds. The Vāyu Purāṇa describes: “Virtue, wisdom, and spiritual clarity predominate. Humanity is naturally aligned with dharma; truthfulness, compassion and self-awareness are inherent.” Society functions harmoniously without the need for extensive laws or enforcement, because the collective Sattva is so dense that deception, confusion, and cruelty lack the field conditions to take root.

Man in this age comprehends the source of universal magnetism with its principle of duality, and his intelligence reaches out to grasp the mystery of Aum, the creative vibration that sustains the universe. The corresponding sphere is Maha Loka, the fourth and highest realm within Māyā—called Daśamadwār, the Door, because it connects the three lower worlds with the three spiritual spheres above. The perfected being who transcends even this sphere passes into Jana Loka, becoming a “Son of God.”', 1),
    (14, 'treta_yuga', 'Tretā Yuga', NULL, 'The Age of Effortful Dharma', 'In Tretā Yuga, truth-consciousness is still the dominant field condition, but a quarter of the ambient clarity has dimmed. For the first time, Dharma is not self-evident—it must be sought and attained through effort. The Vāyu Purāṇa’s description is precise: “Spirituality remains strong but requires effort. Human life becomes more complex compared to Satya Yuga; moral and ethical challenges emerge.” The Rāmāyaṇa unfolds during this period, illustrating that even in an age of high consciousness, the embodied soul must actively choose dharma in the face of temptation, attachment, and exile.

Man in this age extends his knowledge over the attributes of universal magnetism—the positive, negative, and neutralizing electricities and the two poles of creative attraction and repulsion. His intelligence penetrates the mysteries of Svaha Loka, the source and origin of all matter-energies, gross and subtle, enabling comprehension of the universe’s true nature. The corresponding Avidyā is the Illusion of Time (Kāla)—the belief that change is real, that sequence and duration constitute the fundamental fabric of existence.', 2),
    (14, 'dvapara_yuga', 'Dvāpara Yuga', NULL, 'The Age of Divided Knowledge', 'In Dvāpara Yuga, consciousness has descended to the midpoint. Truth and ignorance stand in equal measure—a condition the Vāyu Purāṇa describes with extraordinary precision: “Covetousness, lack of fortitude, trading mentality, war-mindedness, indecision about principles, inter-mixture of castes, indecision about duties—these vices provoked by Rajas and Tamas Guṇas prevail in Dvāpara Age” (58.3-4). The single Veda is now divided into four; knowledge itself has fractured into competing traditions, each claiming authority. The Mahābhārata, including the Bhagavad Gītā, unfolds here—an epic of ethical complexity where the “right” action is never self-evident, where even the noblest warriors face irreducible moral dilemmas.

Man in this age gains comprehension of the electrical attributes—the finer forces and subtler matters of creation. He is called Dwija (twice-born), since his mind has arisen from the grave of pure materialism. He understands that all matter is, in the last analysis, expressions of energy and vibratory force. But this awakening is partial; the Avidyā of Space (Deśa)—the illusion that the Ever-Indivisible is divided—still holds sway. Consciousness operates in the second sphere of creation (Bhuva Loka), called Śūnya, the Vacuum Ordinary.', 3),
    (14, 'kali_yuga', 'Kali Yuga', NULL, 'The Age of Material Entanglement', 'In Kali Yuga, the field of collective consciousness operates at its minimum. The Vāyu Purāṇa’s portrait is unsparing: “Violence, jealousy, falsehood, deception and slaughter of ascetics—these are the characteristics of Kali Age which people inherit” (58.31). “In Kali age creatures are affected by passion and greed. They become violent, deceptive, malicious, hot-tempered, impatient and untruthful” (58.37). Knowledge and power are confined to the world of gross matter (Bhu Loka, the first sphere). Man’s natural state is that of Śūdra, a dependent of Nature, his mind centered on the Avidyā of Atomic Form—the belief that the material, the countable, the measurable is all there is.

Yet the Vāyu Purāṇa also contains an astonishing declaration of hope: “Piety practised for one day in Kali Yuga is equal to that practised for a month in Dvāpara and a year in Tretā Age” (58.47). And at the very nadir: “Due to misery they become indifferent to worldly existence. Due to this despondency and indifference, they begin to ponder. By pondering over they attain the state of equanimity. In the state of equanimity they are enlightened” (58.99-100). The darkness of Kali is itself the womb of transformation.', 4);

-- D14 pole descriptions (12 rows)
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The Inner Presence (Psychic)

At the soul level, the being in Satya equilibrium is a Brahman—a knower of the Creator. The spiritual lesson is not one of struggle or attainment but of sustaining realization. The subtle danger of this age—the one remaining Avidyā—is the illusion of Vibration (Aum) itself: the belief that creation is ultimately real, that the dance of cosmic energy is the final truth rather than a luminous veil over the Uncreated Absolute. The Inner Presence feels like standing at a threshold—behind you, the entire manifest universe hums with beauty; before you, an Incomprehensible Silence that no name can describe. The soul’s work in this age is to cross that threshold without looking back.', 'The body in Satya Yuga equilibrium feels like a finely tuned instrument of transparent sensitivity. There is no chronic tension, no residual heaviness in the limbs. The breath is naturally long and rhythmic—not because one is practicing prāṇāyāma, but because the prāṇic field is so clear that the body breathes itself with the same ease with which a flower opens to sunlight. Longevity is at its maximum. Disease, in the modern sense, does not exist; the body’s subtle energies maintain alignment with the cosmic vibration. When you stand on the earth, you feel the earth’s own pulse through the soles of your feet—not as metaphor but as direct somatic perception. There is a humming quality to physical existence, as though every cell participates in a single, coherent chord.', 'The emotional baseline is śānti (peace) suffused with harṣa (selfless joy). Fear is virtually absent—not suppressed, but absent in the way that darkness is absent when a room is flooded with light. The emotional body does not oscillate between craving and aversion; it rests in a steady, warm luminosity. Relationships are experienced as transparent encounters between consciousnesses that recognize their shared source. There is an emotional quality best described as “recognition without possessiveness”—meeting another being and feeling the same substance in them that you feel in yourself, without the impulse to grasp or merge.', 'Thought in Satya Yuga is not the fragmented, discursive chatter that characterizes later ages. It is more like illumination—a thought arises fully formed, complete with its implications, as though the mind were a still lake reflecting the sky without distortion. The Vāyu Purāṇa notes that a single unified Veda exists in this age; knowledge has not yet been divided into competing scriptures. This is not because people are intellectually simple, but because the cognitive apparatus operates at such high fidelity that truth does not require elaborate argumentation. You see what is true the way you see that the sky is blue—directly, without the mediating apparatus of proof, debate, or rationalization.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 14 AND c.slug = 'satya_yuga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Satya consciousness tips into excess, the soul becomes so identified with the luminosity of truth that it loses its capacity for compassion toward beings still veiled. This manifests as a kind of spiritual absolutism—an intolerance not of evil (which barely exists in this field) but of imperfection. The body becomes hyper-sensitized; environments with even slight Tāmasic density feel physically painful, creating a tendency toward withdrawal and isolation. The emotional tone shifts from warm luminosity to a cooler, more distant radiance—the light of a mountain summit rather than a hearth fire. Cognitively, there is a subtle rigidity: because truth is so self-evident, the mind loses its flexibility, its capacity to entertain partial truths or paradox. The spiritual danger is premature transcendence—the soul may attempt to leave creation entirely before completing its karmic curriculum, creating Saṃskāras of avoidance that will surface in later Yugas as a deep, unexplained aversion to embodied life.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 14 AND c.slug = 'satya_yuga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficiency in a Satya-field context arises when a soul of relatively lower development is born into the age of maximum collective truth. Carried by the cosmic tailwind, this being experiences an existence of ease and beauty without fully comprehending it. The somatic experience is pleasant but somewhat numb—like being warmly dressed in cold weather, you feel comfortable without developing the inner heat that would allow you to withstand the cold alone. The emotional tone is peaceful but passive—an agreeable contentment that lacks the depth of earned equanimity. Cognitively, the being relies on the collective field for clarity rather than developing its own discernment; thoughts feel more like “downloads” than discoveries. The spiritual lesson of this deficiency is that ease is not realization. When the cosmic cycle turns and the field degrades, this soul will find itself profoundly disoriented—possessing a memory of light but no practiced capacity to generate it from within. These are the beings who, in later Yugas, become mystics haunted by a paradise they remember but cannot explain.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 14 AND c.slug = 'satya_yuga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The Inner Presence (Psychic)

The soul in Tretā equilibrium is classified as Bipra, the perfect human class. The spiritual lesson is the conquest of the Illusion of Time—the realization that change is apparent, not ultimate. This is the age of the great yajñas (ritual sacrifices), not as empty ceremony but as conscious acts of aligning individual will with cosmic order. The Inner Presence feels like standing in a hall of mirrors, each reflecting a true aspect of the Absolute but requiring the soul to recognize which is the source and which is the reflection. The work is one of progressive purification—not from evil but from the subtle confusions of multiplicity.', 'The body in Tretā equilibrium still possesses remarkable vitality and longevity, but for the first time, it requires conscious tending. Where Satya bodies self-regulated, Tretā bodies benefit from ritual purification, disciplined diet, and the structured practice of physical austerity (tapas). The somatic signature is one of robust, purposeful energy—the body of an athlete in training rather than the effortless grace of one who has never needed to train. You feel the subtle electrical currents in the spine and limbs; the seven attributes of Chittwa (the universal Heart Atom) are somatically palpable as warmth, vibration, and light in the centers of the body. But these must be cultivated through the regulation of breath and the guidance of a Guru.', 'The emotional baseline remains predominantly sāttvic, but for the first time, an undercurrent of rājasic yearning is detectable—a sense that something must be accomplished, that the soul has a mission requiring effort. This creates a characteristic emotional texture of “earnest striving”—not anxious, not desperate, but purposeful. Devotion (Bhakti) emerges as a natural emotional response to the felt distance between the self and the Absolute that was seamless in Satya. The Rāmāyaṇa’s emotional register—duty, sacrifice, devotion in exile, reunion deferred—captures this perfectly. Love in Tretā is still luminous, but it carries the first weight of longing.', 'The single Veda of Satya still exists but is now beginning to be organized into branches, reflecting the mind’s new tendency to analyze and differentiate. Intelligence in Tretā is keen and penetrating; it grasps the principles of Buddhi (Intelligence, the magnetic pole of attraction that determines truth) and Manas (Mind, the pole of repulsion that produces the ideal world for enjoyment). But these seven attributes of the magnetic Heart now appear as seven distinct “colors”—what was unified perception in Satya begins to separate into spectrum. Thought is still trustworthy, but it now requires discrimination (viveka)—the conscious act of distinguishing truth from near-truth.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 14 AND c.slug = 'treta_yuga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Tretā consciousness tips into excess, the noble quality of effortful dharma curdles into spiritual perfectionism and ritual obsession. The body becomes hyper-disciplined—asceticism pursued not for liberation but for the power it confers. The emotional current shifts from earnest devotion to competitive piety; one begins to measure one’s spiritual attainment against others. Cognitively, the love of discrimination becomes hypercritical judgment—a mind that can see the flaw in every teaching, every teacher, every tradition, without being able to rest in any of them. The Vāyu Purāṇa warns that even in this luminous age, “no man under Māyā, even in Satya Yuga, can fully understand” the sealed book of creation. The excess of Tretā consciousness is the illusion of having understood. The soul accumulates Saṃskāras of spiritual pride that will manifest in later Yugas as an inexplicable contempt for the “spiritual marketplace”—a correct instinct misapplied.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 14 AND c.slug = 'treta_yuga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficiency in a Tretā field manifests as a soul that has the ambient support for spiritual effort but lacks the inner fire to engage. The body is healthy but underutilized; the capacity for tapas lies dormant. Emotionally, there is a pleasant but shallow devotion—attending the rituals, singing the hymns, but without the inner combustion that transforms ritual into realization. Cognitively, the being accepts the teachings of the age without the personal discrimination to penetrate them. The spiritual lesson is that proximity to truth is not truth itself. These souls, in later incarnations, will carry a deep familiarity with spiritual forms—they will be drawn to temples, rituals, and sacred music—but without understanding why. The familiarity will feel like home, but a home they cannot quite enter.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 14 AND c.slug = 'treta_yuga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The Inner Presence (Psychic)

The soul in Dvāpara equilibrium stands at the crossroads. The spiritual lesson is the conquest of the Illusion of Space—the realization that the divisions perceived by the mind (between self and other, between competing truths, between matter and spirit) are apparent, not ultimate. The Inner Presence feels like being in two places at once: one foot in the familiar world of material form, the other in a shimmering landscape of energy and interconnection that you can sense but not yet fully inhabit. The Vāyu Purāṇa’s image is apt: this is the “vacuum ordinary”—a space that appears empty to the gross senses but is, in reality, vibrating with subtle force. The soul’s work is to develop the organs of perception that can navigate this intermediate realm.', 'The body in Dvāpara equilibrium has lost the transparent luminosity of earlier ages but has gained a compensatory density and resilience. The somatic signature is one of alert readiness—the body of someone who knows that the environment is no longer uniformly benign. Physical vitality is still substantial but must be actively maintained through discipline. For the first time, disease appears as a genuine field phenomenon; the Vāyu Purāṇa notes “diseases, sickness, greed” among Dvāpara’s characteristics. The body’s subtle energy can still be felt—particularly through meditation and scriptural practice—but it is no longer the ambient hum of earlier ages. It must be summoned. You feel energy in moments of concentrated practice, then watch it dissipate as you return to daily activity. This oscillation between clarity and cloudiness is the somatic signature of the 50/50 field.', 'The emotional landscape of Dvāpara is defined by ambivalence—the simultaneous presence of noble aspiration and ignoble desire. The Vāyu Purāṇa’s phrase “indecision about principles” is not intellectual weakness; it is the accurate emotional experience of a consciousness caught between two equally powerful gravitational fields. Arjuna on the battlefield of Kurukṣetra, paralyzed between duty and compassion, frozen between action and renunciation, is the archetypal emotional figure of Dvāpara. The emotional current oscillates between utsuka (eagerness to understand) and viṣāda (despondency at the complexity of what one finds). Attachment and desire increase, the texts note—not as moral failures but as natural consequences of a field in which truth and illusion are equipoised.', 'This is the age of the great intellectual proliferation. The Vāyu Purāṇa is explicit: “There are variations and alterations in Ayurveda, Jyotiṣa, and the ancillaries of the Vedas; there are doubts and variations in regard to texts on political economy and logic. Separate systems and schools are established” (58.23-24). The cognitive experience is one of overwhelming information—every tradition presents a compelling case, and the mind cannot rest in any single framework. This is both the challenge and the gift of Dvāpara: the very multiplicity of perspectives forces the development of viveka (discrimination) at a depth that was unnecessary in earlier ages. The Gītā emerges precisely here because this is the age that most desperately needs it—a teaching that cuts through the forest of competing claims to deliver a unified vision of action, knowledge, and devotion.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 14 AND c.slug = 'dvapara_yuga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Dvāpara consciousness tips into excess, the noble quality of discernment becomes intellectual paralysis or partisan fanaticism. The mind, overwhelmed by the proliferation of competing scriptures, either freezes in perpetual analysis or seizes upon one system with defensive fervor. The emotional current of ambivalence hardens into faction—the “war-mindedness” noted by the Vāyu Purāṇa. The body reflects this cognitive warfare: chronic tension in the jaw and shoulders, the somatic signature of a consciousness perpetually braced for argument. The spiritual danger is the Saṃskāra of righteous combat—the soul begins to identify with its intellectual position as though it were its very identity, creating deep grooves of ideological attachment that will persist across lifetimes. In later Yugas, these souls become the passionate advocates—brilliant, articulate, and subtly miserable because they have mistaken the map for the territory.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 14 AND c.slug = 'dvapara_yuga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficiency in a Dvāpara field manifests as the soul that retreats from the complexity. Overwhelmed by the cacophony of competing claims, it withdraws into a simplistic materialism or a comforting spiritual tradition without engaging the deep discriminative work the age demands. The body feels heavy and sluggish—not from physical disease but from the weight of unprocessed cognitive-emotional complexity. The emotional tone is a low-grade confusion that sometimes masquerades as contentment. The spiritual lesson is that complexity is not the enemy; avoidance is. These souls, in later incarnations, will carry a subtle allergy to intellectual depth—a tendency to shut down when faced with nuance, paradox, or competing perspectives, gravitating instead toward whatever offers the simplest narrative.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 14 AND c.slug = 'dvapara_yuga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'The Inner Presence (Psychic)

The soul in Kali equilibrium inhabits what might be called a compressed potential. The spiritual substance is there—“even in this challenging epoch, short, sincere spiritual practices—chanting, devotion, and selfless action—retain the power to awaken the soul”—but it is encased in layers of ambient noise, material distraction, and collective Tāmasic pressure. The Inner Presence feels like a pilot light in a strong wind: still burning, still capable of igniting a full flame, but requiring constant protection. The spiritual lesson of Kali is perhaps the most profound of all the Yugas: that the smallest genuine act of truth in an age of falsehood is worth more than a lifetime of practice in an age of light. One day of Kali piety equals a month of Dvāpara and a year of Tretā. The darkness is the leverage.', 'The body in Kali Yuga, even at equilibrium, carries a baseline of tension that earlier ages would find extraordinary. Lifespan has contracted dramatically; the Vāyu Purāṇa notes a maximum of approximately one hundred years. The somatic signature is density with restlessness—the body feels heavy, gravitationally bound, yet simultaneously agitated by the Rajasic-Tāmasic field. In equilibrium, this manifests as a manageable oscillation: periods of physical lethargy alternating with bursts of nervous energy. The body’s subtle energies are not lost—they are buried. Even brief, sincere spiritual practice can temporarily reactivate them. A Kali-age body in equilibrium is one that has found a sustainable rhythm of practice: daily meditation, chanting, or selfless action that keeps the prāṇic channels minimally clear against the constant pressure of the ambient field to close them.', 'The emotional baseline of Kali equilibrium is a managed tension between fear and hope. The Vāyu Purāṇa’s phrase “perpetual fear of hunger” extends beyond physical want to an existential insecurity—the sense that the ground beneath one’s feet is never quite solid. In equilibrium, this is counterbalanced by a stubborn devotional quality—the knowledge, carried perhaps from higher-Yuga Saṃskāras, that something real exists beyond the material chaos. The emotional texture resembles what the mystics call “dark faith”—faith that persists not because of evidence but despite its absence. Love in Kali equilibrium is fierce, protective, and sometimes desperate; it knows it must hold tight or lose what it cherishes to the centrifugal forces of the age.', 'The mind in Kali equilibrium faces a paradoxical cognitive landscape: an overwhelming abundance of information combined with a profound scarcity of wisdom. The Vāyu Purāṇa’s description of Dvāpara’s “multiplicity of scriptures” has, by Kali, metastasized into total epistemological fragmentation. “The Vedas will be seen in some places and not seen in some places” (58.63)—knowledge itself becomes unreliable, intermittent, contested. In equilibrium, the mind responds by developing a compensatory sharpness: the ability to find the signal in enormous noise, to extract the essential teaching from a sea of distortion. This is why the Gītā’s counsel to “abandon all varieties of dharma and simply surrender” (BG 18.66) has particular potency in Kali—the mind, exhausted by complexity, is finally ready to let go.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 14 AND c.slug = 'kali_yuga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Kali consciousness tips into excess, the Vāyu Purāṇa’s grim portrait becomes the norm rather than the extreme. The body is ravaged by “fatal diseases” and “perpetual danger of drought.” The somatic experience is one of siege—the body feels besieged by toxins, stress, and the accumulated violence of an age in which “people kill and destroy children in wombs” and “beasts of prey become more numerous and powerful.” The emotional current is dominated by raw survival instincts: “passion and greed” unchecked by any countervailing Sattva. Cognitively, vision is “blurred and rendered perverse”—the mind loses the ability to distinguish truth from propaganda, signal from noise, genuine teaching from “persons in the guise of sages.” The spiritual catastrophe of Kali excess is total identification with the body and its survival—Jiveshana (the craving for self-preservation) becomes the only operational drive, extinguishing all higher aspiration under the weight of existential terror.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 14 AND c.slug = 'kali_yuga';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Deficiency in a Kali field is, paradoxically, the beginning of liberation. This is the state described in the Vāyu Purāṇa’s remarkable verses on the end of Kali: “They reach the limit of misery. Only a few of them survive. They are oppressed by old age, sickness and hunger. Due to misery they become indifferent to worldly existence” (58.99). When even the survival instinct exhausts itself, when Kali consciousness becomes too depleted to sustain its own materialism, something unexpected occurs: “Due to this despondency and indifference, they begin to ponder. By pondering over they attain the state of equanimity. In the state of equanimity they are enlightened. Due to enlightenment they become pious” (58.100). The deficiency of Kali—its utter inability to deliver the happiness it promises—becomes the very mechanism of transcendence. The body, stripped to its essentials, discovers it needs less than it believed. The emotional current, drained of craving, finds a strange peace in nirveda (dispassion). The mind, exhausted by false knowledge, becomes receptive to simple truth. This is the cosmic secret hidden in the darkest age: when everything that is not real has been tried and found wanting, what remains is the Real.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 14 AND c.slug = 'kali_yuga';

-- -----------------------------------------------------------------------------
-- D15 — Tridosha  (3 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (15, 'va_ta', 'Vāta', NULL, 'The Principle of Movement', 'Element Basis: Ākāsha (Ether) + Vāyu (Air) · Qualities: Dry, Light, Cold, Rough, Subtle, Mobile · Seat: Colon, Pelvis, Thighs, Ears, Bones, Skin

Vāta is the principle of movement itself. Wherever something moves in the body—a nerve impulse traveling down an axon, the rhythmic expansion and contraction of the lungs, the peristaltic wave that pushes food through the gut, the flutter of an eyelid—Vāta is the governing force. It is the dosha of communication, transport, and initiation. In the Charaka Saṃhitā, it is called the “controller” of the other two doshas, because without movement, neither transformation (Pitta) nor cohesion (Kapha) can occur. Vāta sets things in motion; it is the breath before the word, the impulse before the act.

Its five subdoshas—Prāṇa (governing mind, senses, and vital breath), Udāna (governing speech, effort, and upward movement), Samāna (governing intestinal peristalsis and nutrient absorption), Apāna (governing elimination and downward movement), and Vyāna (governing circulation and peripheral sensation)—together orchestrate the entire kinetic life of the organism. On the psychological plane, Vāta is the energy of creativity, spontaneity, enthusiasm, and the restless hunger for new experience.

T

h

e

s

c

e

n

a

r

i

o

:

I

t

i

s

1

1

P

M

o

n

a

T

u

e

s

d

a

y

.

A

f

r

e

e

l

a

n

c

e

g

r

a

p

h

i

c

d

e

s

i

g

n

e

r

h

a

s

a

p

o

r

t

f

o

l

i

o

s

u

b

m

i

s

s

i

o

n

d

u

e

a

t

m

i

d

n

i

g

h

t

.

T

h

e

d

e

s

i

g

n

i

s

8

0

%

c

o

m

p

l

e

t

e

b

u

t

t

h

e

f

i

n

a

l

e

l

e

m

e

n

t

s

a

r

e

n

o

t

c

o

m

i

n

g

t

o

g

e

t

h

e

r

.

T

h

e

a

p

a

r

t

m

e

n

t

i

s

c

o

l

d

.

T

h

e

r

e

h

a

s

b

e

e

n

n

o

p

r

o

p

e

r

d

i

n

n

e

r

—

o

n

l

y

c

o

f

f

e

e

a

n

d

a

h

a

n

d

f

u

l

o

f

a

l

m

o

n

d

s

s

i

n

c

e

3

P

M

.

S

c

e

n

a

r

i

o

A

:

T

h

e

B

i

n

d

i

n

g

P

a

t

h

(

L

o

w

E

p

i

s

t

e

m

i

c

I

n

t

e

g

r

i

t

y

)

I

n

t

e

r

n

a

l

L

a

n

d

s

c

a

p

e

:

H

e

r

h

a

n

d

s

a

r

e

t

r

e

m

b

l

i

n

g

s

l

i

g

h

t

l

y

,

t

h

o

u

g

h

s

h

e

t

e

l

l

s

h

e

r

s

e

l

f

i

t

i

s

j

u

s

t

t

h

e

c

o

l

d

.

T

h

e

t

r

u

t

h

,

w

h

i

c

h

s

h

e

w

i

l

l

n

o

t

n

a

m

e

,

i

s

t

h

a

t

s

h

e

i

s

t

e

r

r

i

f

i

e

d

—

n

o

t

o

f

t

h

e

d

e

a

d

l

i

n

e

i

t

s

e

l

f

,

b

u

t

o

f

a

f

o

r

m

l

e

s

s

d

r

e

a

d

t

h

a

t

t

h

e

w

o

r

k

i

s

n

o

t

g

o

o

d

e

n

o

u

g

h

,

t

h

a

t

s

h

e

i

s

n

o

t

g

o

o

d

e

n

o

u

g

h

,

t

h

a

t

t

h

i

s

s

u

b

m

i

s

s

i

o

n

w

i

l

l

e

x

p

o

s

e

s

o

m

e

f

u

n

d

a

m

e

n

t

a

l

i

n

a

d

e

q

u

a

c

y

s

h

e

h

a

s

b

e

e

n

o

u

t

r

u

n

n

i

n

g

f

o

r

y

e

a

r

s

.

S

h

e

l

a

b

e

l

s

t

h

i

s

f

e

e

l

i

n

g

“

p

e

r

f

e

c

t

i

o

n

i

s

m

”

a

n

d

w

e

a

r

s

i

t

l

i

k

e

a

b

a

d

g

e

.

“

I

j

u

s

t

c

a

r

e

t

o

o

m

u

c

h

a

b

o

u

t

q

u

a

l

i

t

y

,

”

s

h

e

t

e

l

l

s

h

e

r

s

e

l

f

,

s

c

r

o

l

l

i

n

g

t

h

r

o

u

g

h

a

c

o

m

p

e

t

i

t

o

r

’

s

I

n

s

t

a

g

r

a

m

f

o

r

t

h

e

f

i

f

t

h

t

i

m

e

i

n

a

n

h

o

u

r

.

T

h

e

a

n

x

i

e

t

y

i

s

n

o

w

i

n

d

i

s

t

i

n

g

u

i

s

h

a

b

l

e

f

r

o

m

t

h

e

c

a

f

f

e

i

n

e

.

H

e

r

s

t

o

m

a

c

h

c

r

a

m

p

s

,

b

u

t

s

h

e

i

g

n

o

r

e

s

i

t

—

e

a

t

i

n

g

n

o

w

w

o

u

l

d

“

w

a

s

t

e

t

i

m

e

.

”

C

o

n

d

u

c

t

(

A

̄

g

a

m

i

K

a

r

m

a

)

:

S

h

e

s

c

r

a

p

s

t

h

e

n

e

a

r

-

f

i

n

i

s

h

e

d

d

e

s

i

g

n

a

n

d

s

t

a

r

t

s

o

v

e

r

f

r

o

m

s

c

r

a

t

c

h

a

t

1

1

:

1

5

P

M

.

T

h

e

n

e

w

d

i

r

e

c

t

i

o

n

i

s

m

o

r

e

a

m

b

i

t

i

o

u

s

,

m

o

r

e

c

o

m

p

l

e

x

—

a

p

e

r

f

e

c

t

v

e

h

i

c

l

e

f

o

r

h

e

r

s

c

a

t

t

e

r

e

d

,

u

n

g

r

o

u

n

d

e

d

e

n

e

r

g

y

t

o

b

u

r

n

i

t

s

e

l

f

o

u

t

.

S

h

e

s

u

b

m

i

t

s

a

t

1

1

:

5

8

w

i

t

h

a

v

e

r

s

i

o

n

t

h

a

t

i

s

t

e

c

h

n

i

c

a

l

l

y

f

l

a

s

h

i

e

r

b

u

t

c

o

n

c

e

p

t

u

a

l

l

y

i

n

c

o

h

e

r

e

n

t

.

S

h

e

c

o

l

l

a

p

s

e

s

i

n

t

o

b

e

d

a

t

1

A

M

,

w

i

r

e

d

a

n

d

e

x

h

a

u

s

t

e

d

,

h

e

r

m

i

n

d

s

t

i

l

l

c

y

c

l

i

n

g

t

h

r

o

u

g

h

e

v

e

r

y

t

h

i

n

g

s

h

e

s

h

o

u

l

d

h

a

v

e

d

o

n

e

d

i

f

f

e

r

e

n

t

l

y

.

O

u

t

c

o

m

e

(

S

a

m

̣

s

k

a

̄

r

a

R

e

i

n

f

o

r

c

e

m

e

n

t

)

:

T

h

e

g

r

o

o

v

e

d

e

e

p

e

n

s

:

c

r

i

s

i

s

b

e

c

o

m

e

s

h

e

r

d

e

f

a

u

l

t

c

r

e

a

t

i

v

e

m

o

d

e

.

T

h

e

s

a

m

̣

s

k

a

̄

r

a

t

h

a

t

h

e

r

v

a

l

u

e

i

s

p

r

o

v

e

n

t

h

r

o

u

g

h

l

a

s

t

-

m

i

n

u

t

e

v

i

r

t

u

o

s

i

t

y

h

a

r

d

e

n

s

.

E

a

c

h

r

e

p

e

t

i

t

i

o

n

m

a

k

e

s

t

h

e

n

e

x

t

c

y

c

l

e

m

o

r

e

i

n

t

e

n

s

e

,

m

o

r

e

d

e

p

l

e

t

i

n

g

.

T

h

e

V

a

t

a

e

x

c

e

s

s

c

o

m

p

o

u

n

d

s

:

t

h

e

i

r

r

e

g

u

l

a

r

e

a

t

i

n

g

,

t

h

e

d

i

s

r

u

p

t

e

d

s

l

e

e

p

,

t

h

e

c

h

r

o

n

i

c

l

o

w

-

g

r

a

d

e

f

e

a

r

a

l

l

a

c

c

u

m

u

l

a

t

e

.

T

h

e

L

o

k

a

-

v

a

̄

s

a

n

a

̄

(

c

r

a

v

i

n

g

f

o

r

e

x

t

e

r

n

a

l

v

a

l

i

d

a

t

i

o

n

t

h

r

o

u

g

h

w

o

r

k

)

t

i

g

h

t

e

n

s

i

t

s

g

r

i

p

,

a

n

d

s

h

e

c

a

n

n

o

t

s

e

e

t

h

a

t

t

h

e

“

p

e

r

f

e

c

t

i

o

n

i

s

m

”

i

s

a

c

t

u

a

l

l

y

a

n

x

i

e

t

y

w

e

a

r

i

n

g

a

f

l

a

t

t

e

r

i

n

g

m

a

s

k

.

S

c

e

n

a

r

i

o

B

:

T

h

e

L

i

b

e

r

a

t

i

n

g

P

a

t

h

(

H

i

g

h

E

p

i

s

t

e

m

i

c

I

n

t

e

g

r

i

t

y

)

I

n

t

e

r

n

a

l

L

a

n

d

s

c

a

p

e

:

A

t

1

0

:

4

5

P

M

,

s

h

e

p

a

u

s

e

s

.

S

h

e

n

o

t

i

c

e

s

t

h

e

t

r

e

m

b

l

i

n

g

i

n

h

e

r

h

a

n

d

s

.

S

h

e

n

o

t

i

c

e

s

t

h

e

h

o

l

l

o

w

a

c

h

e

i

n

h

e

r

s

t

o

m

a

c

h

,

t

h

e

r

a

c

i

n

g

q

u

a

l

i

t

y

o

f

h

e

r

t

h

o

u

g

h

t

s

,

t

h

e

c

o

l

d

i

n

h

e

r

f

e

e

t

.

I

n

s

t

e

a

d

o

f

l

a

b

e

l

i

n

g

t

h

i

s

“

p

e

r

f

e

c

t

i

o

n

i

s

m

,

”

s

h

e

n

a

m

e

s

i

t

a

c

c

u

r

a

t

e

l

y

:

“

I

a

m

a

f

r

a

i

d

.

I

a

m

h

u

n

g

r

y

.

I

a

m

c

o

l

d

.

M

y

V

a

̄

t

a

i

s

t

h

r

o

u

g

h

t

h

e

r

o

o

f

.

”

T

h

i

s

m

o

m

e

n

t

o

f

h

o

n

e

s

t

o

b

s

e

r

v

a

t

i

o

n

—

t

h

i

s

r

e

f

u

s

a

l

t

o

d

r

e

s

s

t

h

e

e

x

p

e

r

i

e

n

c

e

i

n

a

m

o

r

e

f

l

a

t

t

e

r

i

n

g

c

o

s

t

u

m

e

—

i

s

t

h

e

p

i

v

o

t

p

o

i

n

t

.

S

h

e

d

o

e

s

n

o

t

j

u

d

g

e

t

h

e

f

e

a

r

.

S

h

e

s

i

m

p

l

y

s

e

e

s

i

t

,

t

h

e

w

a

y

y

o

u

m

i

g

h

t

n

o

t

i

c

e

a

s

t

r

o

n

g

w

i

n

d

b

l

o

w

i

n

g

o

u

t

s

i

d

e

a

w

i

n

d

o

w

.

I

t

i

s

w

e

a

t

h

e

r

,

n

o

t

i

d

e

n

t

i

t

y

.

C

o

n

d

u

c

t

(

P

i

v

o

t

t

o

w

a

r

d

t

h

e

P

a

t

h

o

f

K

a

r

m

a

Y

o

g

a

)

:

S

h

e

s

t

a

n

d

s

u

p

,

p

u

t

s

o

n

w

a

r

m

s

o

c

k

s

,

h

e

a

t

s

a

b

o

w

l

o

f

l

e

f

t

o

v

e

r

d

a

l

a

n

d

r

i

c

e

—

w

a

r

m

,

g

r

o

u

n

d

i

n

g

,

s

l

i

g

h

t

l

y

o

i

l

y

,

t

h

e

e

x

a

c

t

m

e

d

i

c

i

n

e

f

o

r

a

g

g

r

a

v

a

t

e

d

V

a

̄

t

a

.

S

h

e

e

a

t

s

s

l

o

w

l

y

,

s

e

a

t

e

d

.

T

h

e

n

s

h

e

r

e

t

u

r

n

s

t

o

t

h

e

d

e

s

k

,

l

o

o

k

s

a

t

t

h

e

8

0

%

-

c

o

m

p

l

e

t

e

d

e

s

i

g

n

w

i

t

h

f

r

e

s

h

e

y

e

s

,

a

n

d

r

e

c

o

g

n

i

z

e

s

t

h

a

t

i

t

i

s

s

o

l

i

d

.

I

t

i

s

n

o

t

t

r

a

n

s

c

e

n

d

e

n

t

,

b

u

t

i

t

i

s

h

o

n

e

s

t

a

n

d

c

o

m

p

e

t

e

n

t

.

S

h

e

m

a

k

e

s

t

h

r

e

e

s

m

a

l

l

r

e

f

i

n

e

m

e

n

t

s

a

n

d

s

u

b

m

i

t

s

a

t

1

1

:

3

0

w

i

t

h

t

h

i

r

t

y

m

i

n

u

t

e

s

t

o

s

p

a

r

e

.

S

h

e

p

e

r

f

o

r

m

s

a

s

i

m

p

l

e

b

o

d

y

s

c

a

n

b

e

f

o

r

e

b

e

d

,

l

a

n

d

i

n

g

h

e

r

a

t

t

e

n

t

i

o

n

i

n

h

e

r

f

e

e

t

,

h

e

r

b

e

l

l

y

,

h

e

r

h

a

n

d

s

.

O

u

t

c

o

m

e

(

S

a

m

̣

s

k

a

̄

r

a

E

x

h

a

u

s

t

i

o

n

)

:

T

h

e

o

l

d

g

r

o

o

v

e

—

“

m

y

w

o

r

t

h

d

e

p

e

n

d

s

o

n

p

r

o

d

u

c

i

n

g

b

r

i

l

l

i

a

n

c

e

u

n

d

e

r

i

m

p

o

s

s

i

b

l

e

p

r

e

s

s

u

r

e

”

—

i

s

n

o

t

f

e

d

t

o

n

i

g

h

t

.

I

n

s

t

e

a

d

,

a

q

u

i

e

t

e

r

s

a

m

̣

s

k

a

̄

r

a

i

s

p

l

a

n

t

e

d

:

“

s

u

f

f

i

c

i

e

n

t

e

f

f

o

r

t

,

h

o

n

e

s

t

l

y

a

s

s

e

s

s

e

d

,

i

s

e

n

o

u

g

h

.

”

T

h

e

e

s

́

a

n

a

̄

o

f

v

a

l

i

d

a

t

i

o

n

t

h

r

o

u

g

h

c

r

e

a

t

i

v

e

o

u

t

p

u

t

l

o

o

s

e

n

s

i

t

s

h

o

l

d

b

y

o

n

e

s

m

a

l

l

d

e

g

r

e

e

.

T

h

e

V

a

̄

t

a

i

m

b

a

l

a

n

c

e

b

e

g

i

n

s

t

o

c

o

r

r

e

c

t

a

s

t

h

e

b

o

d

y

r

e

c

e

i

v

e

s

w

a

r

m

t

h

,

n

o

u

r

i

s

h

m

e

n

t

,

a

n

d

t

h

e

p

r

o

f

o

u

n

d

m

e

d

i

c

i

n

e

o

f

s

e

l

f

-

h

o

n

e

s

t

y

.', 1),
    (15, 'pitta', 'Pitta', NULL, 'The Principle of Transformation', 'Element Basis: Agni (Fire) + Āpaḥ (Water) · Qualities: Slightly Oily, Sharp, Hot, Light, Pungent, Spreading, Liquid · Seat: Stomach, Small Intestine, Liver, Spleen, Blood, Eyes, Skin

Pitta is the principle of transformation—the intelligence that converts one thing into another. It is fire tempered by water: not the wild blaze of destruction, but the focused flame of the alchemist’s furnace. Wherever matter is being broken down and reassembled—food into tissue, light into vision, sensory data into meaning, raw experience into understanding—Pitta is the governing force. The Charaka Saṃhitā identifies it with digestion in its broadest sense: not merely the chemical processing of food in the gut, but the metabolic intelligence that operates at every level of the organism.

Its five subdoshas—Pāchaka (governing digestion in the stomach), Rañjaka (governing liver metabolism and blood chemistry), Ālochaka (governing vision and the processing of light), Sādhaka (governing the emotional heart and the subtle transformation of feeling into wisdom), and Bhrājaka (governing skin pigmentation and the transformation of external stimuli)—together orchestrate the entire metabolic life of the organism. On the psychological plane, Pitta is the energy of intellect, ambition, courage, discrimination, and the focused will to achieve.

T

h

e

s

c

e

n

a

r

i

o

:

A

s

e

n

i

o

r

p

r

o

j

e

c

t

m

a

n

a

g

e

r

h

a

s

d

i

s

c

o

v

e

r

e

d

t

h

a

t

a

d

i

r

e

c

t

r

e

p

o

r

t

—

s

o

m

e

o

n

e

s

h

e

p

e

r

s

o

n

a

l

l

y

m

e

n

t

o

r

e

d

a

n

d

p

r

o

m

o

t

e

d

—

h

a

s

b

e

e

n

s

u

b

m

i

t

t

i

n

g

w

o

r

k

t

h

a

t

i

n

c

l

u

d

e

s

m

a

t

e

r

i

a

l

c

o

p

i

e

d

f

r

o

m

a

n

o

t

h

e

r

t

e

a

m

’

s

d

e

l

i

v

e

r

a

b

l

e

s

.

T

h

e

e

v

i

d

e

n

c

e

i

s

c

l

e

a

r

.

S

h

e

m

u

s

t

a

d

d

r

e

s

s

i

t

i

n

t

h

e

i

r

o

n

e

-

o

n

-

o

n

e

m

e

e

t

i

n

g

s

c

h

e

d

u

l

e

d

f

o

r

3

P

M

.

I

t

i

s

a

h

o

t

d

a

y

,

s

h

e

s

k

i

p

p

e

d

l

u

n

c

h

,

a

n

d

h

e

r

s

t

o

m

a

c

h

i

s

b

u

r

n

i

n

g

.

S

c

e

n

a

r

i

o

A

:

T

h

e

B

i

n

d

i

n

g

P

a

t

h

(

L

o

w

E

p

i

s

t

e

m

i

c

I

n

t

e

g

r

i

t

y

)

I

n

t

e

r

n

a

l

L

a

n

d

s

c

a

p

e

:

T

h

e

b

u

r

n

i

n

g

i

n

h

e

r

s

t

o

m

a

c

h

m

i

r

r

o

r

s

t

h

e

b

u

r

n

i

n

g

i

n

h

e

r

m

i

n

d

.

S

h

e

t

e

l

l

s

h

e

r

s

e

l

f

s

h

e

i

s

“

d

i

s

a

p

p

o

i

n

t

e

d

”

a

n

d

“

c

o

n

c

e

r

n

e

d

a

b

o

u

t

s

t

a

n

d

a

r

d

s

,

”

b

u

t

t

h

e

t

r

u

t

h

—

w

h

i

c

h

s

h

e

w

i

l

l

n

o

t

e

x

a

m

i

n

e

—

i

s

t

h

a

t

s

h

e

f

e

e

l

s

p

e

r

s

o

n

a

l

l

y

b

e

t

r

a

y

e

d

.

S

h

e

i

n

v

e

s

t

e

d

h

e

r

r

e

p

u

t

a

t

i

o

n

i

n

t

h

i

s

p

e

r

s

o

n

.

S

h

e

v

o

u

c

h

e

d

f

o

r

t

h

e

m

.

A

n

d

n

o

w

t

h

e

i

r

f

a

i

l

u

r

e

r

e

f

l

e

c

t

s

o

n

h

e

r

.

T

h

e

a

n

g

e

r

s

h

e

f

e

e

l

s

i

s

n

o

t

r

i

g

h

t

e

o

u

s

i

n

d

i

g

n

a

t

i

o

n

a

b

o

u

t

i

n

t

e

l

l

e

c

t

u

a

l

i

n

t

e

g

r

i

t

y

;

i

t

i

s

n

a

r

c

i

s

s

i

s

t

i

c

i

n

j

u

r

y

d

r

e

s

s

e

d

i

n

p

r

o

f

e

s

s

i

o

n

a

l

l

a

n

g

u

a

g

e

.

S

h

e

r

e

h

e

a

r

s

e

s

t

h

e

c

o

n

v

e

r

s

a

t

i

o

n

i

n

h

e

r

h

e

a

d

f

o

r

t

h

e

s

i

x

t

h

t

i

m

e

,

s

h

a

r

p

e

n

i

n

g

h

e

r

p

o

i

n

t

s

l

i

k

e

k

n

i

v

e

s

.

C

o

n

d

u

c

t

(

A

̄

g

a

m

i

K

a

r

m

a

)

:

I

n

t

h

e

m

e

e

t

i

n

g

,

s

h

e

i

s

s

u

r

g

i

c

a

l

.

S

h

e

p

r

e

s

e

n

t

s

t

h

e

e

v

i

d

e

n

c

e

w

i

t

h

d

e

v

a

s

t

a

t

i

n

g

p

r

e

c

i

s

i

o

n

,

l

e

a

v

i

n

g

n

o

r

o

o

m

f

o

r

e

x

p

l

a

n

a

t

i

o

n

o

r

c

o

n

t

e

x

t

.

H

e

r

t

o

n

e

i

s

c

o

n

t

r

o

l

l

e

d

b

u

t

h

e

r

e

n

e

r

g

y

i

s

p

u

n

i

s

h

i

n

g

.

S

h

e

w

a

t

c

h

e

s

t

h

e

j

u

n

i

o

r

c

o

l

l

e

a

g

u

e

’

s

f

a

c

e

c

r

u

m

b

l

e

a

n

d

f

e

e

l

s

a

s

h

a

r

p

,

g

u

i

l

t

y

s

a

t

i

s

f

a

c

t

i

o

n

t

h

a

t

s

h

e

i

m

m

e

d

i

a

t

e

l

y

r

e

l

a

b

e

l

s

a

s

“

j

u

s

t

i

c

e

.

”

S

h

e

a

s

s

i

g

n

s

a

f

o

r

m

a

l

r

e

p

r

i

m

a

n

d

a

n

d

e

n

d

s

t

h

e

m

e

e

t

i

n

g

t

e

n

m

i

n

u

t

e

s

e

a

r

l

y

.

O

u

t

c

o

m

e

(

S

a

m

̣

s

k

a

̄

r

a

R

e

i

n

f

o

r

c

e

m

e

n

t

)

:

T

h

e

g

r

o

o

v

e

o

f

“

m

y

w

o

r

t

h

i

s

m

y

s

t

a

n

d

a

r

d

s

,

a

n

d

a

n

y

f

a

i

l

u

r

e

n

e

a

r

m

e

i

s

a

t

h

r

e

a

t

t

o

m

y

i

d

e

n

t

i

t

y

”

d

e

e

p

e

n

s

.

T

h

e

p

i

t

t

a

e

x

c

e

s

s

c

o

m

p

o

u

n

d

s

:

t

h

e

s

k

i

p

p

e

d

l

u

n

c

h

,

t

h

e

b

u

r

n

i

n

g

s

t

o

m

a

c

h

,

t

h

e

c

o

r

t

i

s

o

l

f

r

o

m

r

e

h

e

a

r

s

i

n

g

t

h

e

c

o

n

f

r

o

n

t

a

t

i

o

n

a

l

l

a

f

t

e

r

n

o

o

n

.

T

h

e

c

o

l

l

e

a

g

u

e

,

n

o

w

h

u

m

i

l

i

a

t

e

d

r

a

t

h

e

r

t

h

a

n

c

o

r

r

e

c

t

e

d

,

b

e

c

o

m

e

s

f

e

a

r

f

u

l

a

n

d

s

e

c

r

e

t

i

v

e

—

t

h

e

o

p

p

o

s

i

t

e

o

f

t

h

e

t

r

a

n

s

p

a

r

e

n

t

c

u

l

t

u

r

e

t

h

e

m

a

n

a

g

e

r

c

l

a

i

m

s

t

o

w

a

n

t

.

T

h

e

L

o

̄

k

a

-

v

a

̄

s

a

n

a

̄

(

c

r

a

v

i

n

g

f

o

r

t

h

e

w

o

r

l

d

’

s

r

e

c

o

g

n

i

t

i

o

n

o

f

h

e

r

c

o

m

p

e

t

e

n

c

e

)

t

i

g

h

t

e

n

s

.

T

h

e

l

o

n

e

l

i

n

e

s

s

o

f

e

x

c

e

l

l

e

n

c

e

,

w

h

i

c

h

s

h

e

m

i

s

t

a

k

e

s

f

o

r

t

h

e

p

r

i

c

e

o

f

i

n

t

e

g

r

i

t

y

,

g

r

o

w

s

.

S

c

e

n

a

r

i

o

B

:

T

h

e

L

i

b

e

r

a

t

i

n

g

P

a

t

h

(

H

i

g

h

E

p

i

s

t

e

m

i

c

I

n

t

e

g

r

i

t

y

)

I

n

t

e

r

n

a

l

L

a

n

d

s

c

a

p

e

:

A

t

2

:

3

0

P

M

,

s

h

e

p

a

u

s

e

s

.

S

h

e

n

o

t

i

c

e

s

t

h

e

b

u

r

n

i

n

g

i

n

h

e

r

s

t

o

m

a

c

h

,

t

h

e

h

e

a

t

i

n

h

e

r

f

a

c

e

,

t

h

e

s

h

a

r

p

,

p

r

o

s

e

c

u

t

o

r

i

a

l

q

u

a

l

i

t

y

o

f

h

e

r

r

e

h

e

a

r

s

e

d

s

p

e

e

c

h

.

S

h

e

n

a

m

e

s

i

t

h

o

n

e

s

t

l

y

:

“

I

a

m

a

n

g

r

y

,

b

u

t

m

o

r

e

t

h

a

n

a

n

g

r

y

,

I

f

e

e

l

e

x

p

o

s

e

d

.

I

a

m

a

f

r

a

i

d

t

h

i

s

m

a

k

e

s

m

e

l

o

o

k

l

i

k

e

a

p

o

o

r

j

u

d

g

e

o

f

c

h

a

r

a

c

t

e

r

.

M

y

P

i

t

t

a

i

s

d

r

i

v

i

n

g

t

h

i

s

b

u

s

,

a

n

d

i

t

i

s

h

e

a

d

i

n

g

t

o

w

a

r

d

a

c

o

n

v

e

r

s

a

t

i

o

n

t

h

a

t

w

i

l

l

f

e

e

l

s

a

t

i

s

f

y

i

n

g

f

o

r

f

i

v

e

m

i

n

u

t

e

s

a

n

d

t

h

e

n

l

e

a

v

e

w

r

e

c

k

a

g

e

f

o

r

m

o

n

t

h

s

.

”

S

h

e

e

a

t

s

a

l

i

g

h

t

,

c

o

o

l

i

n

g

l

u

n

c

h

—

a

s

a

l

a

d

w

i

t

h

c

u

c

u

m

b

e

r

a

n

d

m

i

n

t

.

S

h

e

d

r

i

n

k

s

c

o

o

l

w

a

t

e

r

.

S

h

e

l

e

t

s

t

h

e

r

e

h

e

a

r

s

e

d

s

p

e

e

c

h

d

i

s

s

o

l

v

e

.

C

o

n

d

u

c

t

(

P

i

v

o

t

t

o

w

a

r

d

t

h

e

P

a

t

h

o

f

J

n

̃

a

̄

n

a

Y

o

g

a

)

:

I

n

t

h

e

m

e

e

t

i

n

g

,

s

h

e

o

p

e

n

s

w

i

t

h

a

q

u

e

s

t

i

o

n

,

n

o

t

a

n

a

c

c

u

s

a

t

i

o

n

:

“

H

e

l

p

m

e

u

n

d

e

r

s

t

a

n

d

h

o

w

t

h

i

s

s

e

c

t

i

o

n

c

a

m

e

t

o

l

o

o

k

s

o

s

i

m

i

l

a

r

t

o

t

h

e

o

t

h

e

r

t

e

a

m

’

s

w

o

r

k

.

”

S

h

e

l

i

s

t

e

n

s

.

T

h

e

e

x

p

l

a

n

a

t

i

o

n

r

e

v

e

a

l

s

n

o

t

m

a

l

i

c

e

b

u

t

a

c

o

m

b

i

n

a

t

i

o

n

o

f

p

o

o

r

t

i

m

e

m

a

n

a

g

e

m

e

n

t

,

i

n

a

d

e

q

u

a

t

e

t

r

a

i

n

i

n

g

o

n

c

i

t

a

t

i

o

n

p

r

o

t

o

c

o

l

s

,

a

n

d

g

e

n

u

i

n

e

i

g

n

o

r

a

n

c

e

o

f

t

h

e

b

o

u

n

d

a

r

y

.

S

h

e

a

d

d

r

e

s

s

e

s

t

h

e

i

s

s

u

e

c

l

e

a

r

l

y

b

u

t

w

i

t

h

o

u

t

t

h

e

p

u

n

i

s

h

i

n

g

e

n

e

r

g

y

:

“

T

h

i

s

c

a

n

n

o

t

h

a

p

p

e

n

a

g

a

i

n

.

H

e

r

e

i

s

w

h

y

.

A

n

d

h

e

r

e

i

s

t

h

e

s

u

p

p

o

r

t

I

a

m

g

o

i

n

g

t

o

p

u

t

i

n

p

l

a

c

e

t

o

m

a

k

e

s

u

r

e

i

t

d

o

e

s

n

’

t

.

”

O

u

t

c

o

m

e

(

S

a

m

̣

s

k

a

̄

r

a

E

x

h

a

u

s

t

i

o

n

)

:

T

h

e

o

l

d

g

r

o

o

v

e

—

“

f

a

i

l

u

r

e

n

e

a

r

m

e

m

u

s

t

b

e

m

e

t

w

i

t

h

t

h

e

f

u

l

l

f

o

r

c

e

o

f

m

y

j

u

d

g

m

e

n

t

”

—

i

s

n

o

t

f

e

d

t

o

n

i

g

h

t

.

A

n

e

w

i

m

p

r

e

s

s

i

o

n

f

o

r

m

s

:

“

C

l

a

r

i

t

y

w

i

t

h

o

u

t

c

r

u

e

l

t

y

i

s

m

o

r

e

p

o

w

e

r

f

u

l

t

h

a

n

p

r

e

c

i

s

i

o

n

d

e

p

l

o

y

e

d

a

s

a

w

e

a

p

o

n

.

”

T

h

e

e

s

́

a

n

a

̄

o

f

b

e

i

n

g

s

e

e

n

a

s

i

n

f

a

l

l

i

b

l

e

l

o

o

s

e

n

s

i

t

s

g

r

i

p

b

y

o

n

e

q

u

i

e

t

d

e

g

r

e

e

.

T

h

e

P

i

t

t

a

i

m

b

a

l

a

n

c

e

b

e

g

i

n

s

t

o

c

o

r

r

e

c

t

:

t

h

e

b

o

d

y

c

o

o

l

s

,

t

h

e

s

t

o

m

a

c

h

s

e

t

t

l

e

s

,

a

n

d

t

h

e

r

e

l

a

t

i

o

n

s

h

i

p

w

i

t

h

t

h

e

j

u

n

i

o

r

c

o

l

l

e

a

g

u

e

—

w

h

i

l

e

n

o

w

m

o

r

e

b

o

u

n

d

a

r

i

e

d

—

i

s

s

t

r

e

n

g

t

h

e

n

e

d

r

a

t

h

e

r

t

h

a

n

s

h

a

t

t

e

r

e

d

.', 2),
    (15, 'kapha', 'Kapha', NULL, 'The Principle of Cohesion', 'Element Basis: Āpaḥ (Water) + Pṛthivī (Earth) · Qualities: Heavy, Slow, Cool, Oily, Smooth, Dense, Soft, Stable, Gross, Sticky · Seat: Chest, Throat, Lungs, Head, Stomach, Joints, Lymph, Fat Tissue

Kapha is the principle of cohesion—the force that holds things together. If Vāta is the wind and Pitta is the fire, then Kapha is the earth and water that give the organism its substance, its weight, its durability. Wherever structures are maintained, tissues are lubricated, memories are stored, or emotional bonds are sustained, Kapha is the governing force. It is the dosha of stability, endurance, and love in its most unconditional form.

Its five subdoshas—Kledaka (governing the mucous lining of the stomach), Avalambaka (governing the lungs, heart, and trachea), Bodhaka (governing saliva and taste), Tarpaka (governing cerebrospinal fluid and the “lubrication” of the brain), and Śleṣaka (governing joint fluid, connective tissue, and the sinovial membranes)—together orchestrate the entire structural and preservative life of the organism. On the psychological plane, Kapha is the energy of patience, loyalty, compassion, emotional stability, and the deep, enduring forms of love and memory.

T

h

e

s

c

e

n

a

r

i

o

:

A

4

8

-

y

e

a

r

-

o

l

d

h

i

g

h

s

c

h

o

o

l

g

u

i

d

a

n

c

e

c

o

u

n

s

e

l

o

r

h

a

s

w

o

r

k

e

d

a

t

t

h

e

s

a

m

e

s

c

h

o

o

l

f

o

r

t

w

e

n

t

y

-

t

w

o

y

e

a

r

s

.

H

e

i

s

b

e

l

o

v

e

d

b

y

s

t

u

d

e

n

t

s

a

n

d

c

o

l

l

e

a

g

u

e

s

a

l

i

k

e

f

o

r

h

i

s

p

a

t

i

e

n

c

e

a

n

d

d

e

p

e

n

d

a

b

i

l

i

t

y

.

T

h

e

d

i

s

t

r

i

c

t

h

a

s

o

f

f

e

r

e

d

h

i

m

a

p

r

o

m

o

t

i

o

n

t

o

D

i

r

e

c

t

o

r

o

f

S

t

u

d

e

n

t

S

e

r

v

i

c

e

s

a

t

t

h

e

c

o

u

n

t

y

l

e

v

e

l

—

a

r

o

l

e

w

i

t

h

m

o

r

e

i

m

p

a

c

t

,

m

o

r

e

v

i

s

i

b

i

l

i

t

y

,

a

n

d

a

s

i

g

n

i

f

i

c

a

n

t

p

a

y

r

a

i

s

e

.

H

e

h

a

s

t

h

r

e

e

w

e

e

k

s

t

o

d

e

c

i

d

e

.

H

i

s

w

i

f

e

i

s

e

x

c

i

t

e

d

.

H

e

h

a

s

t

o

l

d

n

o

o

n

e

t

h

a

t

e

v

e

r

y

t

i

m

e

h

e

t

h

i

n

k

s

a

b

o

u

t

a

c

c

e

p

t

i

n

g

,

h

i

s

c

h

e

s

t

t

i

g

h

t

e

n

s

a

n

d

h

i

s

a

p

p

e

t

i

t

e

d

i

s

a

p

p

e

a

r

s

.

S

c

e

n

a

r

i

o

A

:

T

h

e

B

i

n

d

i

n

g

P

a

t

h

(

L

o

w

E

p

i

s

t

e

m

i

c

I

n

t

e

g

r

i

t

y

)

I

n

t

e

r

n

a

l

L

a

n

d

s

c

a

p

e

:

H

e

t

e

l

l

s

h

i

m

s

e

l

f

h

e

i

s

b

e

i

n

g

“

t

h

o

u

g

h

t

f

u

l

”

a

n

d

“

c

a

r

e

f

u

l

.

”

H

e

f

r

a

m

e

s

h

i

s

r

e

s

i

s

t

a

n

c

e

a

s

w

i

s

d

o

m

:

“

I

k

n

o

w

w

h

a

t

I

h

a

v

e

h

e

r

e

.

T

h

e

s

t

u

d

e

n

t

s

d

e

p

e

n

d

o

n

m

e

.

W

h

y

f

i

x

w

h

a

t

i

s

n

’

t

b

r

o

k

e

n

?

”

B

u

t

t

h

e

t

r

u

t

h

—

w

h

i

c

h

h

e

w

i

l

l

n

o

t

n

a

m

e

—

i

s

t

h

a

t

h

e

i

s

t

e

r

r

i

f

i

e

d

.

T

h

e

n

e

w

r

o

l

e

w

o

u

l

d

r

e

q

u

i

r

e

h

i

m

t

o

l

e

a

r

n

n

e

w

s

y

s

t

e

m

s

,

m

a

n

a

g

e

a

d

u

l

t

s

i

n

s

t

e

a

d

o

f

c

h

i

l

d

r

e

n

,

p

r

e

s

e

n

t

t

o

s

c

h

o

o

l

b

o

a

r

d

s

,

n

a

v

i

g

a

t

e

p

o

l

i

t

i

c

a

l

d

y

n

a

m

i

c

s

.

I

t

w

o

u

l

d

r

e

q

u

i

r

e

h

i

m

t

o

b

e

a

b

e

g

i

n

n

e

r

a

g

a

i

n

,

a

n

d

t

h

e

K

a

p

h

a

i

n

h

i

m

w

o

u

l

d

r

a

t

h

e

r

e

a

t

g

l

a

s

s

t

h

a

n

b

e

a

b

e

g

i

n

n

e

r

.

T

h

e

t

i

g

h

t

n

e

s

s

i

n

h

i

s

c

h

e

s

t

i

s

n

o

t

c

a

r

e

f

u

l

c

o

n

s

i

d

e

r

a

t

i

o

n

;

i

t

i

s

t

h

e

p

h

y

s

i

c

a

l

s

e

n

s

a

t

i

o

n

o

f

a

c

o

n

s

c

i

o

u

s

n

e

s

s

t

h

a

t

h

a

s

f

u

s

e

d

w

i

t

h

i

t

s

c

o

m

f

o

r

t

z

o

n

e

a

n

d

i

s

n

o

w

g

r

i

p

p

i

n

g

i

t

w

i

t

h

t

h

e

d

e

s

p

e

r

a

t

e

s

t

r

e

n

g

t

h

o

f

s

o

m

e

o

n

e

w

h

o

b

e

l

i

e

v

e

s

t

h

e

y

w

i

l

l

d

i

e

i

f

t

h

e

y

l

e

t

g

o

.

C

o

n

d

u

c

t

(

A

̄

g

a

m

i

K

a

r

m

a

)

:

H

e

l

e

t

s

t

h

e

t

h

r

e

e

w

e

e

k

s

s

l

i

d

e

b

y

w

i

t

h

o

u

t

m

a

k

i

n

g

a

d

e

c

i

s

i

o

n

,

w

h

i

c

h

i

s

i

t

s

e

l

f

a

d

e

c

i

s

i

o

n

.

H

e

t

e

l

l

s

h

i

s

w

i

f

e

h

e

“

j

u

s

t

n

e

e

d

s

m

o

r

e

t

i

m

e

”

a

n

d

s

c

h

e

d

u

l

e

s

a

m

e

e

t

i

n

g

w

i

t

h

t

h

e

d

i

s

t

r

i

c

t

s

u

p

e

r

i

n

t

e

n

d

e

n

t

t

h

a

t

h

e

c

a

n

c

e

l

s

t

w

i

c

e

.

I

n

t

h

e

e

v

e

n

i

n

g

s

,

h

e

m

e

d

i

c

a

t

e

s

t

h

e

a

n

x

i

e

t

y

w

i

t

h

c

o

m

f

o

r

t

f

o

o

d

—

p

a

s

t

a

,

b

r

e

a

d

,

i

c

e

c

r

e

a

m

—

a

n

d

f

a

l

l

s

a

s

l

e

e

p

o

n

t

h

e

c

o

u

c

h

w

a

t

c

h

i

n

g

o

l

d

t

e

l

e

v

i

s

i

o

n

s

e

r

i

e

s

h

e

h

a

s

s

e

e

n

a

d

o

z

e

n

t

i

m

e

s

.

W

h

e

n

t

h

e

d

e

a

d

l

i

n

e

p

a

s

s

e

s

,

h

e

f

e

e

l

s

a

w

a

s

h

o

f

r

e

l

i

e

f

t

h

a

t

h

e

m

i

s

t

a

k

e

s

f

o

r

p

e

a

c

e

.

O

u

t

c

o

m

e

(

S

a

m

̣

s

k

a

̄

r

a

R

e

i

n

f

o

r

c

e

m

e

n

t

)

:

T

h

e

g

r

o

o

v

e

o

f

“

s

a

f

e

t

y

e

q

u

a

l

s

s

t

a

y

i

n

g

w

h

e

r

e

I

a

m

”

d

e

e

p

e

n

s

i

n

t

o

a

r

u

t

.

T

h

e

s

a

m

̣

s

k

a

̄

r

a

o

f

i

d

e

n

t

i

f

y

i

n

g

s

t

a

b

i

l

i

t

y

w

i

t

h

s

t

a

s

i

s

h

a

r

d

e

n

s

.

H

i

s

w

i

f

e

’

s

d

i

s

a

p

p

o

i

n

t

m

e

n

t

,

w

h

i

c

h

s

h

e

d

o

e

s

n

o

t

h

i

d

e

,

b

e

c

o

m

e

s

a

n

e

w

s

o

u

r

c

e

o

f

d

u

l

l

,

u

n

p

r

o

c

e

s

s

e

d

g

u

i

l

t

t

h

a

t

s

e

t

t

l

e

s

i

n

t

o

t

h

e

r

e

l

a

t

i

o

n

s

h

i

p

l

i

k

e

s

e

d

i

m

e

n

t

.

T

h

e

K

a

p

h

a

e

x

c

e

s

s

c

o

m

p

o

u

n

d

s

:

t

h

e

h

e

a

v

y

e

v

e

n

i

n

g

e

a

t

i

n

g

,

t

h

e

p

a

s

s

i

v

e

e

n

t

e

r

t

a

i

n

m

e

n

t

,

t

h

e

a

v

o

i

d

a

n

c

e

o

f

c

h

a

l

l

e

n

g

e

a

l

l

t

h

i

c

k

e

n

t

h

e

f

o

g

o

f

s

t

a

g

n

a

t

i

o

n

.

T

h

e

D

e

h

a

-

v

a

̄

s

a

n

a

̄

(

i

d

e

n

t

i

f

i

c

a

t

i

o

n

w

i

t

h

b

o

d

i

l

y

c

o

m

f

o

r

t

)

a

n

d

L

o

̄

k

a

-

v

a

̄

s

a

n

a

̄

(

i

d

e

n

t

i

f

i

c

a

t

i

o

n

w

i

t

h

h

i

s

r

o

l

e

a

s

“

t

h

e

d

e

p

e

n

d

a

b

l

e

o

n

e

”

)

t

i

g

h

t

e

n

t

h

e

i

r

h

o

l

d

,

a

n

d

h

e

c

a

n

n

o

t

s

e

e

t

h

a

t

h

i

s

g

r

e

a

t

e

s

t

s

t

r

e

n

g

t

h

—

h

i

s

s

t

e

a

d

f

a

s

t

n

e

s

s

—

h

a

s

b

e

c

o

m

e

h

i

s

m

o

s

t

e

l

a

b

o

r

a

t

e

p

r

i

s

o

n

.

S

c

e

n

a

r

i

o

B

:

T

h

e

L

i

b

e

r

a

t

i

n

g

P

a

t

h

(

H

i

g

h

E

p

i

s

t

e

m

i

c

I

n

t

e

g

r

i

t

y

)

I

n

t

e

r

n

a

l

L

a

n

d

s

c

a

p

e

:

M

i

d

w

a

y

t

h

r

o

u

g

h

t

h

e

t

h

r

e

e

w

e

e

k

s

,

h

e

s

i

t

s

i

n

h

i

s

e

m

p

t

y

o

f

f

i

c

e

a

f

t

e

r

t

h

e

l

a

s

t

s

t

u

d

e

n

t

h

a

s

g

o

n

e

a

n

d

a

l

l

o

w

s

h

i

m

s

e

l

f

t

o

f

e

e

l

w

h

a

t

i

s

a

c

t

u

a

l

l

y

t

h

e

r

e

.

H

e

d

o

e

s

n

o

t

r

e

a

c

h

f

o

r

t

h

e

l

a

b

e

l

“

t

h

o

u

g

h

t

f

u

l

.

”

H

e

n

a

m

e

s

i

t

:

“

I

a

m

a

f

r

a

i

d

.

I

a

m

a

f

r

a

i

d

o

f

f

a

i

l

i

n

g

a

t

s

o

m

e

t

h

i

n

g

n

e

w

.

I

a

m

a

f

r

a

i

d

o

f

b

e

i

n

g

u

n

c

o

m

f

o

r

t

a

b

l

e

.

I

a

m

a

f

r

a

i

d

o

f

l

o

s

i

n

g

t

h

e

i

d

e

n

t

i

t

y

I

h

a

v

e

b

u

i

l

t

h

e

r

e

o

v

e

r

t

w

e

n

t

y

-

t

w

o

y

e

a

r

s

.

”

T

h

e

n

a

m

i

n

g

d

o

e

s

n

o

t

e

l

i

m

i

n

a

t

e

t

h

e

f

e

a

r

,

b

u

t

i

t

c

h

a

n

g

e

s

h

i

s

r

e

l

a

t

i

o

n

s

h

i

p

t

o

i

t

.

T

h

e

f

e

a

r

i

s

n

o

l

o

n

g

e

r

d

i

s

g

u

i

s

e

d

a

s

w

i

s

d

o

m

;

i

t

i

s

j

u

s

t

f

e

a

r

—

a

h

e

a

v

y

,

c

o

l

d

w

e

i

g

h

t

i

n

h

i

s

b

e

l

l

y

t

h

a

t

i

s

r

e

c

o

g

n

i

z

a

b

l

y

,

c

h

a

r

a

c

t

e

r

i

s

t

i

c

a

l

l

y

K

a

p

h

a

.

C

o

n

d

u

c

t

(

P

i

v

o

t

t

o

w

a

r

d

t

h

e

P

a

t

h

o

f

B

h

a

k

t

i

Y

o

g

a

)

:

H

e

c

a

l

l

s

h

i

s

w

i

f

e

t

h

a

t

e

v

e

n

i

n

g

a

n

d

s

a

y

s

,

h

o

n

e

s

t

l

y

,

“

I

a

m

s

c

a

r

e

d

.

N

o

t

o

f

t

h

e

j

o

b

—

o

f

t

h

e

c

h

a

n

g

e

.

”

H

e

r

r

e

s

p

o

n

s

e

—

n

o

t

a

d

v

i

c

e

,

j

u

s

t

p

r

e

s

e

n

c

e

—

c

r

a

c

k

s

s

o

m

e

t

h

i

n

g

o

p

e

n

.

H

e

s

p

e

n

d

s

t

h

e

n

e

x

t

w

e

e

k

i

n

g

e

n

u

i

n

e

d

i

s

c

e

r

n

m

e

n

t

,

n

o

t

a

v

o

i

d

a

n

c

e

:

h

e

v

i

s

i

t

s

t

h

e

c

o

u

n

t

y

o

f

f

i

c

e

,

t

a

l

k

s

t

o

t

h

e

p

e

r

s

o

n

w

h

o

c

u

r

r

e

n

t

l

y

h

o

l

d

s

t

h

e

r

o

l

e

,

w

r

i

t

e

s

d

o

w

n

h

i

s

f

e

a

r

s

a

n

d

h

i

s

h

o

p

e

s

i

n

t

w

o

c

o

l

u

m

n

s

.

H

e

a

c

c

e

p

t

s

t

h

e

p

o

s

i

t

i

o

n

n

o

t

b

e

c

a

u

s

e

t

h

e

f

e

a

r

h

a

s

d

i

s

a

p

p

e

a

r

e

d

b

u

t

b

e

c

a

u

s

e

h

e

h

a

s

s

e

e

n

c

l

e

a

r

l

y

t

h

a

t

t

h

e

f

e

a

r

i

s

a

s

i

g

n

a

l

o

f

g

r

o

w

t

h

,

n

o

t

o

f

d

a

n

g

e

r

.

H

e

c

h

o

o

s

e

s

d

i

s

c

o

m

f

o

r

t

i

n

s

e

r

v

i

c

e

o

f

a

l

a

r

g

e

r

p

u

r

p

o

s

e

—

a

q

u

i

e

t

a

c

t

o

f

d

e

v

o

t

i

o

n

t

o

t

h

e

p

o

s

s

i

b

i

l

i

t

y

t

h

a

t

h

e

m

i

g

h

t

b

e

m

o

r

e

t

h

a

n

t

h

e

c

o

m

f

o

r

t

a

b

l

e

,

s

a

f

e

v

e

r

s

i

o

n

o

f

h

i

m

s

e

l

f

.

O

u

t

c

o

m

e

(

S

a

m

̣

s

k

a

̄

r

a

E

x

h

a

u

s

t

i

o

n

)

:

T

h

e

o

l

d

g

r

o

o

v

e

—

“

s

t

a

y

i

n

g

w

h

e

r

e

I

a

m

e

q

u

a

l

s

s

a

f

e

t

y

,

a

n

d

s

a

f

e

t

y

e

q

u

a

l

s

l

o

v

e

”

—

i

s

n

o

t

f

e

d

t

o

n

i

g

h

t

.

A

n

e

w

i

m

p

r

e

s

s

i

o

n

f

o

r

m

s

:

“

I

c

a

n

b

e

a

f

r

a

i

d

a

n

d

s

t

i

l

l

c

h

o

o

s

e

t

o

g

r

o

w

.

”

T

h

e

e

s

́

a

n

a

̄

o

f

b

o

d

i

l

y

a

n

d

s

o

c

i

a

l

c

o

m

f

o

r

t

l

o

o

s

e

n

s

i

t

s

g

r

i

p

.

T

h

e

K

a

p

h

a

i

m

b

a

l

a

n

c

e

b

e

g

i

n

s

t

o

c

o

r

r

e

c

t

n

o

t

t

h

r

o

u

g

h

a

s

c

e

t

i

c

d

e

p

r

i

v

a

t

i

o

n

b

u

t

t

h

r

o

u

g

h

t

h

e

i

n

t

r

o

d

u

c

t

i

o

n

o

f

t

h

e

o

n

e

q

u

a

l

i

t

y

K

a

p

h

a

m

o

s

t

n

e

e

d

s

a

n

d

m

o

s

t

r

e

s

i

s

t

s

:

m

o

v

e

m

e

n

t

.

T

h

e

m

o

v

e

m

e

n

t

h

e

r

e

i

s

n

o

t

p

h

y

s

i

c

a

l

b

u

t

e

x

i

s

t

e

n

t

i

a

l

—

t

h

e

w

i

l

l

i

n

g

n

e

s

s

t

o

l

e

t

t

h

e

r

i

v

e

r

o

f

l

i

f

e

c

a

r

r

y

y

o

u

i

n

t

o

n

e

w

t

e

r

r

i

t

o

r

y

.', 3);

-- D15 pole descriptions (9 rows)
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Internal Landscape

Somatic Base (Physical): The body feels light but not ungrounded. There is an effortless quality to movement—limbs respond crisply, digestion proceeds with quiet regularity, the breath flows in a gentle, unforced rhythm. Joints are supple without being hypermobile. The skin, while naturally on the drier side, maintains a healthy glow. There is a pleasant coolness to the hands and feet that feels refreshing rather than uncomfortable. Sleep comes easily and, while perhaps lighter than a Kapha constitution’s deep slumber, it is restorative. The nervous system is alert without being hypervigilant—like a well-tuned instrument, it registers stimuli accurately and responds proportionately.

Emotional Current (Vital): The dominant emotional tone is one of creative enthusiasm. There is a natural buoyancy, a sense that possibilities are everywhere and that life is interesting. This is not the driven intensity of Pitta’s ambition but a lighter, more playful engagement—the delight of a mind that makes unexpected connections. Socially, there is a genuine warmth and a gift for conversation; the Vāta-balanced person is often the one who puts a room at ease with a well-timed observation or a spontaneous laugh. Fear, when it arises, is appropriate and quickly processed—the healthy startle that keeps you alert, not the lingering dread that steals your sleep.

Cognitive Map (Mental): Thought is quick, flexible, and associative. The balanced Vāta mind excels at brainstorming, at seeing patterns across disparate domains, and at initiating projects with infectious optimism. There is a natural adaptability—when plans change, this mind pivots without excessive distress. Memory may not have the photographic precision of a Pitta mind, but it captures the essential thread of an experience with vivid sensory detail. The internal narrative is forward-looking: “What if we tried this?” “I wonder what would happen if…”

Inner Presence (Psychic): At the soul level, balanced Vāta is the experience of prāṇa as grace—the feeling that the life-force is moving through you unimpeded, that you are a channel rather than a dam. There is a natural attunement to subtle energies: the shift of seasons, the emotional atmosphere of a room, the unspoken needs of another person. This is the dosha most closely connected to the Prāṇamaya Kośa (vital sheath), and in equilibrium, it grants an almost intuitive sense of being carried by something larger than oneself. The spiritual lesson is one of trust in the flow—the understanding that not everything needs to be controlled or predicted for life to unfold beautifully.

External Conduct

At work, the balanced Vāta individual is the idea generator, the one who sees the unconventional angle that everyone else missed. They are excellent communicators, adept at translating complex ideas into accessible language. In relationships, they bring spontaneity, humor, and a genuine curiosity about their partner’s inner world. Their daily habits tend toward variety—they may eat different things each day, take different routes to work, and maintain a social calendar that is full but not frantic. Exercise choices lean toward activities that are rhythmic and grounding: walking, gentle yoga, swimming. They manage their energy wisely, knowing instinctively that their constitution requires more rest and regularity than others might need.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 15 AND c.slug = 'va_ta';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Internal Landscape

Somatic Base (Physical): The lightness that was once liberating now becomes a kind of brittle fragility. The body dries out—skin roughens, lips crack, joints begin to click and pop with a new stiffness. Digestion becomes erratic: bloating, gas, and constipation replace the quiet regularity of the balanced state. Sleep fragments; you wake at 2 AM with a racing mind and cannot return to rest. The hands and feet are not just cool but cold, and the cold feels like it has seeped into the bones. There is a quality of restlessness in the muscles themselves—a twitching, a trembling, a sense that the body cannot quite settle. Weight drops involuntarily; the face becomes more angular, the eyes more prominent. The nervous system is now hypervigilant, registering every sound, every movement, every slight change in environment as a potential threat.

Emotional Current (Vital): The buoyancy has become anxiety—a persistent, free-floating apprehension that attaches itself to whatever is at hand. It is the feeling of a spinning top that has lost its axis: the energy is still there, but it has no center to organize around. Fear is no longer appropriate and proportional; it is now a background hum that colors everything. The creative enthusiasm has tipped into scattered hyperactivity—you start twelve projects and finish none, not from laziness but from a nervous inability to sustain attention on any single thing. Socially, the warmth can become a kind of anxious clinginess, or it can reverse into sudden withdrawal, as the overstimulated system seeks solitude to recover. There is a loneliness to excess Vāta—the feeling of being profoundly ungrounded, as though you might simply blow away.

Cognitive Map (Mental): Thought becomes rapid, fragmented, and repetitive. The associative brilliance of balanced Vāta degrades into rumination—the mind loops endlessly over the same worries, generating catastrophic scenarios with vivid and terrible specificity. Decision-making becomes agonizing: every option spawns a dozen “what-ifs,” and the mind cannot rest in a choice. The internal narrative shifts from “What if we tried?” to “What if it goes wrong?” Memory becomes unreliable—not because information is lost, but because the mind is too agitated to encode new experiences clearly. There is a sense of cognitive overload, as though the bandwidth of the mind has been exceeded.

Inner Presence (Psychic): The soul-level experience of excess Vāta is one of disconnection from ground. The attunement to subtle energies that was once a gift now becomes a liability—you absorb the anxiety of others, you are overwhelmed by stimuli, you cannot distinguish your own feelings from those of the environment. The prāṇa that once felt like grace now feels like a wind that has broken free of its banks. The spiritual lesson that is asking to be learned is embodiment—the return to the body, to the earth, to the simple anchor of physical sensation as a counterweight to the mind’s flight.

External Conduct

At work, the excess Vāta individual becomes unreliable—not from bad intention but from genuine inability to follow through. They overcommit, miss deadlines, and then compensate with bursts of frantic, last-minute effort that leave them depleted. Their communication, once clear and engaging, becomes scattered and tangential; colleagues find it hard to follow their train of thought. In relationships, they oscillate between intense neediness and sudden emotional absence. Their daily habits lose all rhythm: meals are skipped or eaten on the run, sleep schedules dissolve, exercise is either excessive (running, cycling at high intensity) or abandoned entirely. They may develop a craving for stimulants—coffee, sugar, social media—that temporarily mask the depletion but ultimately worsen it.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 15 AND c.slug = 'va_ta';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Internal Landscape

Somatic Base (Physical): When Vāta is deficient, the kinetic principle of the body slows to a crawl. Peristalsis weakens, leading to a sluggish gut and chronic constipation of a different character than excess Vāta—here it is not dryness that stalls the system but sheer lack of propulsive force. Circulation becomes poor, not from cold alone but from insufficient vascular motility. Breathing may become shallow and monotonous, lacking the natural variability that signifies a responsive nervous system. Reflexes are dulled. There is a heaviness that mimics Kapha excess but differs in quality: it is not the heaviness of substance but the heaviness of stagnation, like a river that has stopped flowing and become a murky pool.

Emotional Current (Vital): The creative spark has gone out. What replaces it is not Kapha’s contented stillness but a flat, affectless state—a numbness that is neither peace nor despair but simply the absence of vitality. Enthusiasm evaporates; nothing seems interesting or worth initiating. There is a profound passivity that goes beyond introversion—it is the emotional equivalent of paralysis. Social engagement becomes effortful, not because of anxiety (as in excess Vāta) but because the motivational energy to reach out simply is not there.

Cognitive Map (Mental): The quick, associative mind has gone dark. Thought is slow, effortful, and uncreative. There is a cognitive rigidity that is unusual for a Vāta constitution—the natural flexibility has been replaced by a dull inability to see alternatives. Decision-making is impaired not by excessive options (as in excess) but by an absence of the generative energy needed to even formulate choices. The internal narrative is minimal: not the anxious chatter of excess, but a kind of silence that feels more like shutdown than serenity.

Inner Presence (Psychic): The soul-level experience is one of prāṇic depletion—the life-force itself feels diminished. The subtle sensitivity that characterizes Vāta has withdrawn, leaving a strange opacity where there was once transparency. This is the state the classical texts warn about when they speak of Vāta being “suppressed” by excess Kapha or overwhelmed by chronic exhaustion. The spiritual lesson here is reanimation through purpose—the rediscovery of a reason to move, to breathe, to engage.

External Conduct

At work, the Vāta-deficient individual becomes conspicuously passive. They stop volunteering ideas, stop initiating conversations, and may be perceived as disengaged or checked out. In relationships, they are present in body but absent in spirit—going through the motions without the spark that once animated their connection. Daily habits become rigidly minimal, not from discipline but from lack of impetus to do anything beyond the bare minimum.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 15 AND c.slug = 'va_ta';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Internal Landscape

Somatic Base (Physical): The body runs warm but not hot. Digestion is strong and predictable—hunger arrives at regular intervals and is satisfied cleanly, without lingering heaviness or acid reflux. The skin has a healthy luster, slightly oily but not greasy, with good color. The eyes are bright and penetrating. Musculature is well-defined without being bulky—a medium, athletic build that speaks of efficient metabolism. Sleep is deep and sufficient; six or seven hours feels like enough because the quality is high. There is a natural physical confidence, a sense that the body is a reliable instrument that does what you ask of it.

Emotional Current (Vital): The dominant emotional tone is one of purposeful warmth. There is a natural charisma—the kind of person others look to when a decision needs to be made, not because they are domineering but because their clarity is reassuring. Anger, when it arises, is clean and proportional: it flares in response to genuine injustice and subsides once the situation is addressed. There is a deep sense of fairness, an almost visceral reaction to dishonesty or incompetence. In relationships, the balanced Pitta individual is warm, direct, and loyal—the friend who will tell you the truth even when it is uncomfortable, but who will also be the first to show up when you need help.

Cognitive Map (Mental): Thought is sharp, logical, and goal-directed. The balanced Pitta mind excels at analysis, at breaking complex problems into manageable components, and at executing plans with precision. There is a natural gift for strategy and a preference for efficiency that borders on elegance. The internal narrative is organized around purpose: “What needs to be done? What is the most effective way to do it? How do we measure success?” Memory is excellent, especially for facts, sequences, and arguments.

Inner Presence (Psychic): At the soul level, balanced Pitta is the experience of agni as illumination—the inner fire that burns away confusion and reveals things as they are. There is a natural discrimination (viveka) that allows this person to distinguish signal from noise, essence from appearance, truth from comfortable fiction. This is the dosha most closely connected to the Manomaya Kośa (mental sheath) in its analytic capacity, and in equilibrium, it grants the ability to see clearly without the distortion of wishful thinking or denial. The spiritual lesson is one of right use of power—the understanding that clarity and strength are gifts to be placed in service, not weapons to be wielded for dominance.

External Conduct

At work, the balanced Pitta individual is the natural leader and executor. They set clear goals, delegate effectively, and hold themselves and others to high but reasonable standards. In relationships, they are the anchor—dependable, honest, and capable of deep commitment. Their daily habits are organized and purposeful: meals are regular, exercise is vigorous but structured (competitive sports, strength training, hiking), and leisure time is spent in activities that challenge the mind—reading, debate, strategic games. They manage their fire wisely, knowing that even good combustion needs adequate fuel and rest.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 15 AND c.slug = 'pitta';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Internal Landscape

Somatic Base (Physical): The warmth that was once comfortable becomes oppressive heat. The body runs hot—flushing, sweating disproportionately, and radiating a palpable intensity. Digestion, once the crown jewel of the Pitta constitution, goes into overdrive: acid reflux, heartburn, loose and burning stools, an appetite that is ravenous and irritable if not immediately satisfied. The skin erupts—acne, rashes, rosacea, inflammatory patches that speak of an immune system that has turned its fire inward. The eyes become red, dry, and hypersensitive to light. Headaches arrive with sharp, piercing quality, often behind the eyes. Sleep becomes lighter, more easily disrupted by heat; waking at 2 or 3 AM is common, not with Vāta’s anxious mind but with Pitta’s restless, strategizing brain that cannot stop planning and problem-solving.

Emotional Current (Vital): The purposeful warmth has become anger—not always explosive, but always present as a low, persistent irritability that sharpens into fury at the slightest provocation. The sense of fairness has curdled into judgmentalism; everyone is being measured against a standard they cannot meet, and the dominant inner experience is one of frustrated contempt. Impatience becomes a defining trait: conversations feel too slow, colleagues feel too incompetent, traffic feels like a personal affront. There is a particular Pitta flavor of loneliness that comes from the progressive alienation caused by this intensity—people begin to tiptoe around you, and the resulting distance is experienced not as a consequence of your behavior but as further evidence of their inadequacy.

Cognitive Map (Mental): The sharp, analytical mind has become a weapon—not a tool for understanding but an instrument of domination. Thought is now hyper-critical, finding flaws in everything and everyone. The internal narrative shifts from “What is the most effective approach?” to “Why can’t anyone do this right?” There is an obsessive quality to mental activity: the mind locks onto a problem or a perceived slight and chews on it relentlessly, generating rebuttals, counterarguments, and devastating retorts to conversations that may have ended hours ago. Decision-making becomes autocratic—not because other perspectives are unavailable, but because considering them feels like an intolerable waste of time.

Inner Presence (Psychic): The soul-level experience of excess Pitta is one of agni consuming its own vessel. The discriminative intelligence that was once a lamp has become a forest fire, burning through relationships, health, and inner peace with equal ferocity. The ego has identified completely with its competence and its standards; any failure to meet those standards—in self or others—is experienced as an existential threat. The spiritual lesson that is asking to be learned is surrender of control—the humbling recognition that not everything can be optimized, that imperfection is not a character flaw, and that the purpose of fire is to illuminate, not to incinerate.

External Conduct

At work, the excess Pitta individual becomes the micromanager, the impossible-to-please boss, the colleague who corrects your grammar in a team email. Their leadership, once inspiring, becomes autocratic; people comply out of fear rather than respect. In relationships, they become controlling, critical, and emotionally volatile—the partner who keeps score, who revisits old arguments with forensic precision, who cannot let an imperfection pass without comment. Their daily habits become a regime of optimization that leaves no room for pleasure or spontaneity: every meal is functional, every workout is measured, every interaction is evaluated for efficiency.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 15 AND c.slug = 'pitta';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Internal Landscape

Somatic Base (Physical): When Pitta is deficient, the metabolic fire dims. Digestion becomes weak and incomplete—food sits in the stomach like a stone, not because of Vāta’s erratic peristalsis or Kapha’s excessive mucus, but because the combustive intelligence itself is diminished. The body feels cool when it should feel warm; the skin loses its luster and takes on a pallid, washed-out quality. The eyes, once bright and penetrating, become dull. There may be an inability to tolerate cold that is unusual for a Pitta constitution. Appetite weakens, and with it the body’s ability to extract nutrition from what is consumed. Energy drops—not into Vāta’s wired exhaustion or Kapha’s heavy lethargy, but into a muted, colorless fatigue that lacks even the vitality to feel properly tired.

Emotional Current (Vital): The fire of purpose goes out. What replaces it is not anxiety or heaviness but a grey indifference—a loss of the passionate engagement that defined the Pitta temperament. Decisions that once felt urgent and important now feel arbitrary. The moral clarity dims; right and wrong, which once had sharp edges, blur into a relativistic haze. There is a particular flavor of depression that belongs to deficient Pitta: it is not the sadness of loss but the emptiness of purposelessness. The individual who once organized their life around achievement and contribution now cannot find a reason to get out of bed.

Cognitive Map (Mental): The sharp, analytical mind becomes foggy and uncertain. The ability to discriminate—to see clearly what is true and what is false, what matters and what does not—is compromised. Thought loses its directional quality; there is no internal compass pointing toward a goal. Decision-making is impaired not by Vāta’s excess of options or Kapha’s resistance to change, but by a genuine inability to generate the evaluative heat needed to weigh alternatives. The internal narrative becomes flat: “I don’t know. I don’t care. It doesn’t matter.”

Inner Presence (Psychic): The soul-level experience is one of spiritual amnesia—a forgetting of purpose, of dharma, of the reason the individual came into this life. The inner fire that once illuminated the path forward has gone dark, and the individual is left standing in a landscape they can no longer read. The spiritual lesson here is rekindling through meaningful action—the rediscovery of purpose not through grand ambition but through the simple, faithful performance of small duties that gradually feed the flame back to life.

External Conduct

At work, the Pitta-deficient individual becomes passive and disengaged—a striking contrast to their usual driven nature. They stop setting goals, stop holding standards, and may abdicate leadership responsibilities they once relished. In relationships, they become emotionally unavailable—not from anger or withdrawal but from a genuine absence of the warmth that once defined their connection. Their daily habits lose their purposeful structure: meals are eaten without attention, exercise is abandoned, and the strategic leisure activities are replaced by passive consumption—scrolling, watching, drifting.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 15 AND c.slug = 'pitta';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Internal Landscape

Somatic Base (Physical): The body feels substantial, solid, and deeply comfortable in itself. There is a natural sturdiness—thick bones, well-padded joints, strong muscles that may not be visibly defined but possess remarkable endurance. The skin is smooth, cool, and slightly moist with good elasticity. Hair is thick and lustrous. Digestion is steady if not spectacular—the Kapha constitution processes food slowly but thoroughly, extracting maximum nutrition. Sleep is the crown jewel: deep, restorative, dreamless sleep that leaves the individual genuinely refreshed. The immune system is robust; this is the constitution least likely to fall ill, and when it does, recovery is steady and complete. There is a physical groundedness that others can feel—sitting next to a balanced Kapha individual is like sitting next to a very old, very calm tree.

Emotional Current (Vital): The dominant emotional tone is one of unconditional steadiness. The Kapha temperament in balance is the most emotionally stable of the three—not because they lack feeling but because their feelings are deep, slow-moving, and enduring rather than quick, reactive, and volatile. Love, once given, is not easily withdrawn. Commitments, once made, are held. There is a natural compassion that arises not from intellectual understanding (Pitta) or empathic attunement (Vāta) but from a bone-deep sense of shared humanity. The balanced Kapha individual is the friend you call at 3 AM—not for advice, but for the silent, unshakeable presence that tells you everything will eventually be all right.

Cognitive Map (Mental): Thought is slow, deliberate, and thorough. The Kapha mind does not generate ideas at Vāta’s pace or analyze them with Pitta’s precision, but what it does do is understand them deeply and remember them permanently. This is the constitution with the best long-term memory—not for facts and figures (which belong more to Pitta) but for the emotional texture of experiences, the faces of people met decades ago, the exact quality of a childhood afternoon. Decision-making is careful, sometimes maddeningly so, but the decisions, once made, are wise and rarely regretted. The internal narrative is calm and present-tense: “All is well. There is time. Let me consider this properly.”

Inner Presence (Psychic): At the soul level, balanced Kapha is the experience of pṛthivī as sanctuary—the feeling of being held by the earth, of having a place, of belonging. There is a natural devotional quality to this dosha—a readiness to surrender not from weakness but from a deep trust in the sustaining order of things. This is the dosha most closely connected to the Annamaya Kośa (physical sheath) in its preservative aspect, and in equilibrium, it grants an almost elemental sense of being rooted, as though one’s existence has the same unquestionable reality as a mountain. The spiritual lesson is one of grounded service—the understanding that the highest expression of stability is to become the ground on which others can stand.

External Conduct

At work, the balanced Kapha individual is the one who holds the team together. They may not be the visionary (Vāta) or the strategist (Pitta), but they are the person who remembers every commitment, follows through on every promise, and maintains the institutional memory that keeps the organization functional. In relationships, they are the rock—steady, reliable, affectionate, and deeply present. Their daily habits are the most consistent of the three doshas: regular meals, regular sleep, regular exercise (preferring endurance activities like long walks, swimming, or cycling), and a social life that revolves around a small, intimate circle of deep friendships rather than a wide network.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 15 AND c.slug = 'kapha';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Internal Landscape

Somatic Base (Physical): The sturdiness that was once an asset becomes heaviness. Weight accumulates, especially around the abdomen, hips, and thighs, and resists all efforts at reduction. The body feels waterlogged—puffy, swollen, sluggish. Sinuses congest; there is a chronic, low-grade stuffiness that dulls the senses. The skin, once smooth, becomes oily and congested. Digestion slows to a crawl: food sits in the stomach for hours, producing a dull, heavy fullness that is not quite nausea but removes all appetite for anything other than more heavy, sweet, comforting food—precisely what the imbalance least needs. Sleep, once restorative, becomes excessive; eight hours is not enough, ten is not enough, and waking feels like swimming upward through thick mud. There is a physical inertia that is genuinely alarming to the Kapha individual’s friends, if not to the individual themselves: every movement requires an act of will.

Emotional Current (Vital): The steadiness has become inertia, and the unconditional love has thickened into possessiveness. The emotional landscape of excess Kapha is dominated by attachment—a clinging to people, to habits, to possessions, to the familiar, that is driven by a deep, unacknowledged fear of change. The individual becomes emotionally needy in a way that is smothering rather than nurturing—their care comes with invisible strings, their generosity carries the expectation of reciprocal loyalty. Grief, when it comes, is oceanic and endless; the Kapha constitution, which processes everything slowly, processes loss slowest of all, and may remain stuck in mourning for years. There is a particular flavor of sadness to excess Kapha that is not the sharp anguish of loss but the dull ache of stagnation—the slow suffocation of a life that has stopped growing.

Cognitive Map (Mental): The deliberate mind has become a resistant mind. Change, novelty, and challenge are not just unwelcome but actively threatening. The internal narrative is one of defensive conservatism: “Why change what works? Why risk what we have? Things are fine the way they are.” Decision-making is not just slow but avoidant; the individual will endure remarkable discomfort rather than face the uncertainty of change. Memory, once a gift, becomes a cage—the Kapha mind’s excellent retention means that old hurts, old fears, and old patterns are preserved with high fidelity and replayed with tiresome regularity.

Inner Presence (Psychic): The soul-level experience of excess Kapha is one of spiritual hibernation—the deep sleep of consciousness that has mistaken comfort for peace and routine for practice. The devotional quality that was once a strength has become spiritual passivity: “God will provide” becomes an excuse for not providing for oneself. The earth-connection that was once grounding has become gravity—a force that pulls the individual downward into matter rather than supporting their upward evolution. The spiritual lesson that is asking to be learned is sacred discomfort—the recognition that growth requires leaving the comfortable cave, that love must include the willingness to let go, and that the earth’s purpose is not to hold you down but to give you something firm to push off from.

External Conduct

At work, the excess Kapha individual becomes the person who blocks every initiative, who argues against every change, who creates drag on every project with their need for more data, more meetings, more consensus before any action is taken. In relationships, they become the partner who will not grow—who resists couples counseling, avoids difficult conversations, and substitutes material generosity for emotional engagement. Their daily habits calcify into rigid routines that serve comfort rather than health: the same heavy meals, the same sedentary evenings, the same social patterns—less and less activity, more and more consumption, an ever-narrowing circle of experience.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 15 AND c.slug = 'kapha';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'Internal Landscape

Somatic Base (Physical): When Kapha is deficient, the body loses its structural integrity. Joints dry out and begin to ache—not with Vāta’s sharp, migrating pain but with a deep, bone-level stiffness that speaks of insufficient lubrication. The mucous membranes thin; the throat is chronically dry, the sinuses empty and irritated. Weight drops below what is healthy for the constitution—not into Vāta’s angular thinness but into a kind of wasted quality that suggests the body is consuming its own reserves. The immune system falters; infections linger, wounds heal slowly, and there is a general vulnerability that is new and disturbing. Sleep becomes thin and unrestorative—not from Vāta’s racing mind but from the absence of the deep, nourishing quality that Kapha sleep normally provides.

Emotional Current (Vital): The emotional ground gives way. The steadiness and loyalty that defined the Kapha temperament are replaced by a rootless, insecure quality that the individual finds deeply disorienting. Commitments feel less binding, relationships less sustaining. There is an uncharacteristic restlessness—not Vāta’s creative buzz but a homeless feeling, as though the floor one has always stood on has been pulled away. The capacity for unconditional love thins out; the individual finds themselves calculating rather than giving, measuring rather than trusting—a Pitta-like vigilance that is foreign to their nature and exhausting in practice.

Cognitive Map (Mental): The reliable, steady mind becomes scattered and forgetful—not with Vāta’s fast-moving distraction but with a fog-like quality, as though the memories are still there but can no longer be accessed. The deep comprehension that is Kapha’s cognitive gift is replaced by surface-level processing. The internal narrative takes on an unfamiliar quality of anxiety: “Is anything solid? Can I count on anything? Who will hold things together if I cannot?”

Inner Presence (Psychic): The soul-level experience is one of lost sanctuary—the earth-connection that once provided unshakeable belonging has been severed. The individual feels spiritually homeless in a way that no amount of external comfort can address. This is the state the classical texts warn about when they speak of Kapha being “dried out” by excess Vāta or “burned up” by excess Pitta. The spiritual lesson here is rebuilding the inner home—the patient, deliberate reconstruction of the foundations of trust, stability, and belonging that allow the soul to rest.

External Conduct

At work, the Kapha-deficient individual loses their characteristic reliability. Commitments are dropped, follow-through falters, and the institutional memory they once provided becomes patchy and unreliable. In relationships, they become unexpectedly distant—not from anger but from a genuine inability to access the warmth and steadiness that once defined their presence. Their daily habits become irregular in an un-Kapha way: skipped meals, disrupted sleep, and a restlessness that manifests as aimless activity without the sustaining structure of routine.', NULL, NULL, NULL
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 15 AND c.slug = 'kapha';

-- -----------------------------------------------------------------------------
-- D16 — Inner Nature & Its Law  (2 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (16, 'svabhava', 'Svabhāva', NULL, 'The Structure of Inner Nature', 'Before we can understand what a person is meant to do, we must first understand what a person is. This is the domain of Svabhāva—the “own-becoming” that precedes all action and gives action its distinctive flavor. Sri Aurobindo describes it as “the truth of ourselves, that which is growing in us and finding always new and more adequate forms in birth after birth.” It is not the conditioned personality—the set of habits, preferences, and social masks we acquire through upbringing. It is the soul’s characteristic energy, the particular way the Divine expresses itself through this particular Jīva (individual soul).

The Gītā teaches that this soul-energy has a fourfold character. Every Jīva possesses four “threads” of inner power: the thread of Knowledge (the drive to understand, to see truth, to illuminate); the thread of Heroism (the drive to act with courage, to protect, to lead); the thread of Mutuality (the drive to create, exchange, harmonize, and relate); and the thread of Skill (the drive to serve, to craft, to bring order through labor). In any given person, one thread tends to predominate, giving their inner life its characteristic coloring—its particular way of perceiving, reacting, and finding meaning.

Crucially, Svabhāva is distinct from Prakṛti (the three Guṇas of nature—Sattva, Rajas, Tamas). The Guṇas are the modes through which nature operates—the mechanical apparatus of how we act. Svabhāva is the soul-force behind that apparatus—it is what drives the machine, not the machine itself. A person whose predominant thread is Knowledge may express it through Sattva (serene inquiry), through Rajas (argumentative debate), or even through Tamas (intellectual laziness disguised as “contemplation”). The thread remains the same; the quality of its expression changes.', 1),
    (16, 'svadharma', 'Svadharma', NULL, 'The Law of Right Action', 'If Svabhāva is the structure—the “who”—then Svadharma is the drive—the “what.” It is the law of action that arises naturally when a person’s conduct is rooted in their inner nature. Swami Sri Atmananda puts it precisely: Svadharma is the law of action in conformity with the innate system. The word dharma itself means “that which holds”—the sustaining principle. Svadharma, then, is the pattern of action that holds you together, that prevents the inner dissolution that follows from living against your grain.

The key teaching of the Gītā is that Svadharma is determined not by birth, not by family tradition, not by social convention, but by the inner quality of one’s being. Sri Aurobindo is emphatic on this point: the Gītā’s concept of the four orders of human function has nothing to do with hereditary caste. It has everything to do with the four threads of the soul’s nature. The work of the Brahmin is described not as priestcraft but as “calm, self-control, askesis, purity, long-suffering, candour, knowledge.” The work of the Kshatriya is not administration but “heroism, high spirit, resolution, not fleeing in the battle.” These are inner qualities that find outward expression through whatever occupation the person happens to hold.

This distinction matters enormously for lived experience, because it means that Svadharma is not a fixed destination—it is a living rhythm. Swami Sri Atmananda teaches that the predominant thread of Svabhāva can shift as a person develops spiritually. “What is true at a given time in my life may not be true at another stage of my life,” he says. “It depends upon which thread is now predominant at a given time.” Svadharma, therefore, is not a life sentence. It is a living alignment—a constant, honest calibration of one’s action to one’s evolving nature.', 2);

-- D16 pole descriptions (6 rows)
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When a person is in contact with their Svabhāva—when the inner nature is neither inflated nor suppressed—there is a quality of lived experience that is difficult to describe but unmistakable when felt. It is what the tradition calls sahaja—“that which is born with you.” It is the experience of being at home in your own skin, in your own way of thinking, in the particular rhythm that your life naturally falls into when you stop trying to be someone else.

The Inner Presence (Psychic)

At the deepest level, there is a sense of alignment between the personal will and something larger. The tradition calls this the experience of being a “faultless instrument”—not in the sense of perfection, but in the sense of honest function. A tool used for its intended purpose does not strain. A chisel used to chisel, a lens used to focus, a bridge used to span. The soul, in this state, is doing what it came here to do, and there is a quiet, unshakeable knowing that accompanies this. It is not grandiose. It is simply: this is right.

External Conduct

In daily life, this person works with a natural efficiency that others often find remarkable but which the person themselves experiences as ordinary. Relationships have a quality of generosity because the person is not draining others to compensate for inner emptiness. They can admire someone else’s path without coveting it, celebrate another’s success without comparing. Their work—whether it is teaching, building, governing, or serving—has a signature quality, a distinctive “voice” that cannot be imitated because it emerges from the unique configuration of their soul.

The Vignette: A Morning That Moves

Priya is a documentary filmmaker whose thread of Knowledge predominates. She wakes at 5:30, not from an alarm but from a thought that continued forming in her sleep—a new angle for the story she is editing. She makes tea and sits with her laptop, and the morning has a quality of inevitability to it. She is not “motivating herself.” She is not thinking about whether film is a “sensible” career. The footage unfolds before her, and her mind moves through it the way water moves through a familiar channel—finding the truth of the story because finding truth is what her inner nature does. By 9 AM, she has accomplished more than some manage in a day, and she does not feel depleted. She feels fed.', 'The body feels settled. Not lethargic—settled. There is a particular quality of physical ease that comes when you are doing what you were made to do: the shoulders drop away from the ears, the jaw unclenches, the breath deepens without effort. A person whose predominant thread is Knowledge sits down to study and feels their body quiet, as though the physical system recognizes that this is its proper orientation. A person whose thread is Heroism steps into a situation that demands decisive action and feels an energizing surge—not anxious adrenaline, but a clean, bright alertness that makes the body feel capable and alive. The body, in equilibrium, becomes a willing instrument rather than a resistant obstacle.', 'The emotional tone is one of quiet rightness. It is not euphoria—euphoria is a peak state that burns out. This is more like a steady, warm current that runs beneath the surface of daily activity. There is an absence of the particular emotional static that accompanies self-betrayal: no nagging guilt, no restless itch to be somewhere else, no vague sense that something important is being neglected. Instead, there is a natural enthusiasm—the word’s root, entheos, “god within,” describes it well. The person feels fueled from inside rather than dragged forward by external carrots or pushed by external sticks.', 'The mind is clear about its own orientation. A person in touch with their Svabhāva does not need to constantly justify their choices to themselves. The internal monologue is not dominated by comparison—“She’s doing better than me,” “He has a more respectable path”—because the concept of “better” has been replaced by the concept of “mine.” Decisions arise from an inner logic that feels self-evident rather than labored. This does not mean the mind is free from doubt; it means the doubt is productive—“How can I do this more truly?” rather than “Should I be doing this at all?”'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 16 AND c.slug = 'svabhava';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When one’s predominant thread inflates beyond its natural proportion—when it swallows the other three rather than leading them—the result is a characteristic distortion. The very quality that was a person’s gift becomes their cage. The tradition’s wisdom here is subtle: it is not that the person has too much of a good thing; it is that the good thing has lost its relationship to the whole. A fire that heats the home is useful; the same fire, uncontained, burns the house down.

The Inner Presence (Psychic)

The soul-level experience is one of subtle imprisonment. The person feels powerful in their domain—and yet something is missing. There is a restlessness beneath the competence, a hunger that achievement in the dominant thread cannot satisfy. This is because the other three threads of the Svabhāva are being starved. The soul is four-sided, and living exclusively through one side is like breathing through a single nostril—possible, but suffocating in the long run. The spiritual lesson at play is the difference between specialization (healthy emphasis of one thread) and amputation (the cutting off of the others).

External Conduct

The person becomes difficult to be around in predictable ways. The excess-Knowledge individual talks over people, corrects everyone, and becomes the person at the dinner table who cannot simply enjoy a story without dissecting it. The excess-Heroism individual dominates meetings, overrides consensus, and cannot delegate because no one else’s effort meets their standard. The excess-Mutuality individual over-promises, over-accommodates, and eventually collapses under the weight of commitments made from an inability to say no. The excess-Skill individual is always busy but never available, their relationships threadbare from chronic neglect.

The Vignette: The Scholar Who Forgot to Live

Rohan is a philosophy professor whose thread of Knowledge has consumed the other three. He has published twelve books and can dismantle any argument with surgical precision. But his marriage has hollowed out. His wife stopped trying to talk to him about her day years ago; every conversation became a lecture, every shared feeling an occasion for analysis. At a faculty dinner, a junior colleague makes a passing remark about Kant that Rohan considers imprecise. He spends eleven minutes correcting the error. The table falls silent. Driving home, his wife says nothing. Rohan replays the exchange and feels a flush of satisfaction at having been right—followed immediately by a vast, shapeless loneliness he cannot name. His thread of Mutuality, starved for decades, knocks on a door he no longer knows how to open.', 'The body shows the strain of a single faculty being overworked. The Knowledge-dominant person who has become intellectually hypertrophied feels it as chronic tension in the head and neck—the physical signature of a mind that never stops analyzing. The Heroism-dominant person pushed to excess feels it as a perpetual state of fight-or-flight: jaw clenched, cortisol high, sleep disrupted by the body’s inability to stand down from battle mode. The Mutuality-dominant person in excess develops the somatic markers of over-extension—fatigue from constantly managing relationships, the depleted feeling of someone who gives endlessly without refilling. The body, in each case, is sounding an alarm that the mind refuses to hear.', 'The emotional landscape narrows. Where equilibrium brings a broad emotional palette, excess produces a kind of monochrome intensity. The Knowledge thread in excess generates intellectual Mada (pride)—a sharp, cutting certainty that makes every disagreement feel like an offense against truth. The Heroism thread in excess produces a relentless drive that cannot tolerate passivity in anyone, including oneself—a restless, combative energy that turns every interaction into a contest of will. The Mutuality thread in excess creates emotional enmeshment, a loss of boundaries where you cannot tell where your feelings end and another person’s begin. The Skill thread in excess produces a compulsive workaholism where personal worth is measured entirely by output.', 'The mind becomes rigidly identified with its dominant mode. It confuses one particular way of seeing with the only way of seeing. The Knowledge-dominant person begins to believe that every problem can be solved through analysis, dismissing emotion and intuition as inferior. The Heroism-dominant person believes that every challenge requires force, unable to conceive of patience or yielding as strength. The mind, in this state, loses the flexibility that comes from the interplay of all four threads. It becomes a specialist so narrow that it can no longer see the forest for the trees.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 16 AND c.slug = 'svabhava';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'If excess is the tyranny of one thread, deficiency is the loss of contact with one’s predominant thread altogether. This is the condition the Gītā warns against most urgently: the state of a person who has abandoned their own nature to follow Paradharma—the “other’s law.” It is not simply that they have chosen the wrong career. It is that they have exiled themselves from the deepest structure of their own being. Sri Ramakrishna’s metaphor is precise: it is like taking medicine prescribed for someone else’s disease. Even if the medicine is excellent, it will not cure you. It may, in fact, poison you.

The Inner Presence (Psychic)

At the soul level, there is a feeling of abandonment—but it is self-abandonment. The Jīva has turned away from its own nature, and the nature waits, patient but unfulfilled. Sri Aurobindo describes this as “the vain circuit of the wrong road retarding our real progress.” The soul is not destroyed; it is dormant. The spiritual experience is one of distance—a sense of watching one’s own life from behind glass, performing competently but never touching the real current beneath. The lesson at this level is stark: you cannot outrun who you are. You can only delay the reckoning.

External Conduct

The person may be highly functional—even outwardly impressive. They hold titles, earn salaries, maintain social standing. But there is a quality of mechanical repetition in their conduct. They do not bring creativity or vitality to their work because those qualities live in the thread they have abandoned. Relationships often become transactional—maintained through obligation rather than genuine connection—because the person’s emotional bandwidth is consumed by the internal war between who they are performing to be and who they actually are. Burnout in this state is not caused by overwork. It is caused by misalignment.

The Vignette: The Surgeon Who Should Have Been a Poet

Anand is a cardiac surgeon. He is excellent at what he does—meticulous, precise, respected by his peers. His father was a surgeon. His grandfather was a surgeon. He never questioned the path. But most evenings, after the last operation, he sits in his car in the hospital garage for twenty minutes before driving home. He does not listen to music. He does not check his phone. He sits in a silence that feels like a held breath, and in that silence there is a presence—something wordless and aching and patient—that he has spent thirty years not looking at. On his desk at home, hidden beneath journals, there is a leather notebook filled with lines of poetry he has written since he was fourteen. He has never shown it to anyone. When he holds the notebook, his hands feel different—lighter, more alive—than they ever do in the operating room. His Svabhāva has not left him. It is simply waiting, in a leather notebook, for him to come home.', 'The body feels wrong in a way that has no medical explanation. The classic symptoms are chronic fatigue that sleep does not resolve, a low-grade nausea that appears every Sunday evening before the work week begins, a heaviness in the limbs that lifts mysteriously on vacation. These are not psychosomatic in the dismissive sense. They are the body’s honest report that it is being driven in a direction contrary to its design. The Gītā’s word for this is vināśti—“perdition,” “decay”—the slow dissolution that follows from a life lived against its own grain.', 'The characteristic emotion is a diffuse, nameless dissatisfaction. It is not anger (which at least has energy) and not grief (which at least has an object). It is more like a low-grade existential Nirveda (dejection)—a greyness that coats every experience. Successes feel hollow; compliments slide off the surface without being absorbed. There is a particular flavor of envy that belongs to this state: not the sharp envy of wanting what someone else has, but the dull ache of watching someone live with authenticity and wondering why your own life feels like a well-constructed imitation of something real.', 'The mind is full of borrowed narratives. “I should want this.” “This is what successful people do.” “My parents sacrificed so much for this path; I can’t throw it away.” The internal monologue is dominated by the voices of others—society’s definition of worth, the family’s expectations, the culture’s metrics of success. The person’s own voice, the voice of the Svabhāva, has grown so faint from disuse that they can no longer distinguish it from the noise. This is the cognitive hallmark of Paradharma: the inability to tell the difference between what you want and what you have been told to want.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 16 AND c.slug = 'svabhava';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Svadharma is functioning in its natural state, work ceases to be separate from spiritual life. The Gītā’s phrase is svakarmaṇā tam abhyarcya siddhim vindati mānavaḥ (18.46)—“a person can reach the state of perfect perfection by sincerely pursuing the path ordained for them.” This is not metaphor. It is a description of a specific experiential state in which the boundary between work and worship dissolves.

The Inner Presence (Psychic)

The soul-level experience is one of participation in something larger than oneself. Sri Aurobindo calls this being “not the personal doer of the act, but a spiritual channel of the works of the transcendent and universal Spirit.” In lived experience, this manifests as occasional moments of self-forgetfulness—not dissociation, but a healthy dissolving of the ego’s usual commentary, where the person and the work become, briefly, indistinguishable. These are the moments artists describe as the painting painting itself, or the musician describes as the music playing through them. They are not mystical anomalies. They are the natural fruit of Svadharma practiced with integrity.

External Conduct

The person in Svadharma equilibrium is reliable without rigidity. They show up consistently for their work, but they are not compulsive about it. There is a natural boundary between effort and rest that does not need to be enforced by external rules. Relationships are enriched because the person brings a surplus—a vitality generated by authentic work—rather than the deficit created by labor that drains. They are, in the Gītā’s image, a “faultless instrument”—not perfect, but functioning as designed.

The Vignette: The Gardener’s Saturday

David is a landscape architect whose thread of Mutuality and Skill interweave naturally. On Saturday morning, he kneels in the soil of a community garden he designed for a neighborhood that had none. His hands are in the dirt, and he is showing a teenager how to read the roots of a transplanted shrub. He is not thinking about his portfolio or his billing rate. He is not performing for an audience. The work—connecting people to earth, connecting earth to beauty, connecting beauty to community—is simply happening through him. By afternoon, his back aches and his fingernails are black, and he drives home with a quietness in his chest that feels like gratitude. Not gratitude for anything in particular. Gratitude as a state of being. His Svadharma and his Svabhāva are, for this afternoon, perfectly aligned, and the alignment registers as a kind of prayer the body offers without being asked.', 'The body moves with economy. Actions are clean—no wasted motion, no excessive tension, no bracing against the task. There is a somatic fluidity that athletes call “being in the zone” but which in this context extends beyond peak performance into ordinary daily activity. The carpenter whose Svadharma is craftsmanship feels the wood under their hands as a kind of conversation. The teacher whose Svadharma is illumination feels the rhythm of a classroom as a living pulse. The body, in these moments, is not an obstacle to be overcome but a partner in the work.', 'The dominant emotional quality is what the tradition calls nishkāma—“desireless action.” This is widely misunderstood as apathy. It is the opposite. It is action performed with full engagement but without the anxious attachment to outcome that turns work into a transaction. The emotional experience is one of giving rather than getting. The person does not work in order to receive a reward; the work itself is the reward, and any external recognition is simply a pleasant echo of something already complete within.', 'The mind is oriented toward the intrinsic logic of the work rather than its external metrics. A person following their Svadharma does not primarily ask, “What will this get me?” They ask, “What does this task require of me?” The cognitive frame is one of service to the work itself—a quality that the Gītā describes as making one’s labor a consecration to the Divine. This does not require religious belief. It requires only the recognition that the work has its own integrity, its own demands, and that meeting those demands honestly is a form of self-expression that transcends personal ambition.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 16 AND c.slug = 'svadharma';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When Svadharma moves from a living rhythm into a rigid identity, it ceases to be a path and becomes a prison. This is the subtle danger of finding one’s calling: the calling becomes the whole of one’s identity, and any threat to it—a career disruption, an invitation to explore something new, even a natural developmental shift—is experienced as an existential crisis. The very alignment that was liberating becomes a new form of bondage.

The Inner Presence (Psychic)

The soul is overidentified with its current form. Sri Aurobindo warns against this: “To follow the law of the being does not in the end chain down the soul to any present formulation.” But in excess, that is precisely what happens—the soul becomes chained. The spiritual work at this level is the painful but necessary recognition that Svadharma is a living, evolving rhythm, not a permanent identity. The same person whose Svadharma at thirty was entrepreneurial combat may find, at fifty, that the thread of Knowledge has come forward and their Svadharma now calls them toward teaching or contemplation. To resist this evolution is to turn Svadharma into Paradharma—one’s own past becoming the “other’s path.”

External Conduct

The person becomes increasingly difficult to reach on any frequency other than work. They are the partner who brings the laptop to bed, the parent who misses the recital for the deadline, the friend who cancels every gathering. Their excellence in their domain is real, but it comes at a cost measured in human connection. Over time, the relationships they have neglected wither, and the person finds themselves at the summit of their vocation looking out over a landscape emptied of everything except the work itself.

The Vignette: The Activist at the Breaking Point

Meera has spent twenty years in human rights advocacy. Her thread of Heroism found its natural Svadharma in fighting for the voiceless. But somewhere along the way, the cause consumed the person. She has not taken a vacation in four years. She sleeps with her phone on the pillow, responding to crisis alerts at 3 AM. When her sister invites her to a birthday dinner, Meera says yes but spends the evening on her phone under the table, coordinating a response to a news cycle. Her sister stops inviting her. Meera tells herself this is the price of “important work.” She does not notice that her fury at injustice has curdled into something less noble—a need to fight that has become indistinguishable from a need to be fighting, because fighting is the only state in which she feels real. Her Svadharma has ossified into an identity fortress, and inside the walls, she is exhausted and alone.', 'The body carries the particular tension of someone who cannot stop. Not the scattered busyness of someone who has no center, but the focused, relentless drive of someone who has made their center too tight. Sleep is the first casualty—the mind cannot release its grip on the work long enough to rest. Meals are skipped or eaten absently. The body is treated as a machine to be maintained for the sake of productivity rather than as a dimension of the living self. Chronic stress injuries—repetitive strain, digestive issues, tension headaches—become the body’s protest against its instrumentalization.', 'The emotional world contracts around the work. Joy is only available through the work. Rest feels like failure. Relationships that do not serve the work feel like distractions. There is a characteristic anxiety that belongs to this state: the fear that if the work stops, the self stops—that there is nothing beneath the role. This anxiety is often invisible to the person themselves because they interpret it as “dedication” or “passion.” The tradition would recognize it as a form of Abhinivedsha—the clinging to a particular form of existence as though it were existence itself.', 'The mind has built an airtight narrative around the work: “This is who I am. This is what I was meant to do. Without this, I am nothing.” While the first two statements may be true, the third reveals the distortion. A healthy Svadharma is not the totality of the self; it is the self’s primary expression at a given stage of development. But in excess, the mind confuses the channel with the water—it forgets that the soul’s nature is larger than any single expression of it. This produces a brittle certainty that cracks under the first real challenge to the person’s professional identity.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 16 AND c.slug = 'svadharma';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'This is the Gītā’s gravest warning: the condition of Paradharma, living according to another’s law. Para-dharmaḥ bhayāvahaḥ—“the dharma of another brings fear.” This is not metaphorical fear. It is a specific, somatic, existential dread that permeates the daily life of someone who has taken up a path that does not belong to them—no matter how competent they become at walking it.

The Inner Presence (Psychic)

The deepest pain of Svadharma-deficiency is the experience of self-betrayal. Not betrayal by the world—by family, by society, by circumstance—but by oneself. The soul knows its own nature. It has always known. And the experience of watching oneself, day after day, perform a life that denies that nature is a quiet form of spiritual suffering that no amount of external success can alleviate. This is the “inner friction” the tradition describes: the grinding of gears that were designed for a different mechanism.

External Conduct

The person may be successful by every external measure and yet radiates a subtle, unmistakable flatness. They do their work competently but without signature, without the distinctive quality that emerges when action flows from authentic nature. They are reliable but uninspired. Their relationships, while maintained, often have a quality of going through the motions. Friends and colleagues sense—without being able to articulate it—that the person is not fully present, that something essential is being held back or held elsewhere.

The Vignette: The Conference Room at Twilight

Vikram is a corporate strategy director at a Fortune 100 company. His thread of Knowledge, with its particular bent toward understanding systems and patterns, was meant for research, for inquiry, for the patient unraveling of how things work. Instead, at his father’s urging, he entered the corporate world, where his analytical gifts have made him valuable but never fulfilled. It is 6:30 PM and the conference room has emptied. Vikram sits alone with the quarterly projections on his screen, and for a moment the mask slips. He opens a browser tab and navigates to a university’s astrophysics program—a page he has visited, bookmarked, and closed again more times than he can count. He reads the course descriptions with the hunger of a man looking at photographs of a country he was born in but has never visited. Then he closes the tab, picks up his briefcase, and drives to a house that is paid for, in a neighborhood that is enviable, to a life that is, by every standard except the one that matters, complete.', 'The body carries the weight of perpetual performance. Every action requires a conscious effort that should not be necessary—like a left-handed person forced to write with their right hand, or a sprinter made to run marathons. There is a background exhaustion that is qualitatively different from the tiredness of hard work. It is the tiredness of wrong work—the depletion that comes not from doing too much but from doing what is fundamentally misaligned with one’s design. The body knows the difference, even when the mind refuses to.', 'The predominant emotional experience is bhaya—the fear the Gītā specifically names. It manifests as a low-level, chronic anxiety about being “found out”—not in the modern sense of imposter syndrome (which implies you are the real thing but doubt yourself), but in the deeper sense that you know, at some level beneath articulacy, that this is not your life. This knowledge creates a constant, quiet panic—a feeling of running out of time, of the real life unliving itself in the margins while the performed life occupies center stage.', 'The mind constructs elaborate justifications for the misalignment. “It’s too late to change.” “I have responsibilities.” “This is what adults do—they compromise.” These narratives are not necessarily wrong on the surface; many people do have genuine obligations. But they function, in this context, as walls that prevent the person from hearing the voice of their own nature. The cognitive distortion is not in the content of these thoughts but in their function—they are being used to maintain a state of exile rather than to honestly navigate the tension between obligation and authenticity.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 16 AND c.slug = 'svadharma';

-- -----------------------------------------------------------------------------
-- D17 — Three Lenses  (3 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (17, 'the_adhibhautika_perspective', 'The Adhibhautika Perspective', NULL, '“Life is What Happens Out There”', 'mahābhūtāni ahaṅkāro buddhir avyaktam eva ca

The great elements, ego, intellect, and the unmanifest constitute material nature — Bhagavad Gītā XIII.5

The Adhibhautika lens is the most immediate, the most tangible, and for most people the most dominant orientation in daily life. Through this perspective, the individual sees themselves as a physical entity navigating a physical world populated by other physical entities. Meaning is derived from what can be seen, touched, measured, and transacted. The Taittirīya Upaniṣad connects this orientation to the Annamaya Kośa—the outermost sheath of food and matter—which represents the most accessible layer of selfhood but also the most vulnerable to external disruption.

The person living primarily through this lens experiences life as a series of negotiations with the external environment. Their wellbeing is calibrated to material security, social harmony, and sensory satisfaction. When the environment cooperates, they feel powerful and purposeful. When it resists, they feel besieged. Their characteristic question, faced with any disturbance, is always directed outward: “Who did this to me?”

T

h

e

s

c

e

n

a

r

i

o

:

Y

o

u

h

a

v

e

j

u

s

t

r

e

c

e

i

v

e

d

a

m

i

x

e

d

p

e

r

f

o

r

m

a

n

c

e

r

e

v

i

e

w

a

t

w

o

r

k

.

Y

o

u

r

m

a

n

a

g

e

r

p

r

a

i

s

e

d

y

o

u

r

t

e

c

h

n

i

c

a

l

c

o

n

t

r

i

b

u

t

i

o

n

s

b

u

t

f

l

a

g

g

e

d

y

o

u

r

d

i

f

f

i

c

u

l

t

y

c

o

l

l

a

b

o

r

a

t

i

n

g

w

i

t

h

a

c

r

o

s

s

-

f

u

n

c

t

i

o

n

a

l

t

e

a

m

a

n

d

y

o

u

r

r

e

s

i

s

t

a

n

c

e

t

o

f

e

e

d

b

a

c

k

f

r

o

m

p

e

e

r

s

.

I

n

t

e

r

n

a

l

L

a

n

d

s

c

a

p

e

:

T

h

e

A

d

h

i

b

h

a

u

t

i

k

a

e

x

c

e

s

s

a

c

t

i

v

a

t

e

s

i

m

m

e

d

i

a

t

e

l

y

.

B

e

f

o

r

e

t

h

e

r

e

v

i

e

w

m

e

e

t

i

n

g

h

a

s

e

n

d

e

d

,

y

o

u

r

m

i

n

d

i

s

a

l

r

e

a

d

y

c

o

n

s

t

r

u

c

t

i

n

g

t

h

e

p

r

o

s

e

c

u

t

i

o

n

c

a

s

e

:

“

T

h

i

s

i

s

p

o

l

i

t

i

c

a

l

.

T

h

e

c

r

o

s

s

-

f

u

n

c

t

i

o

n

a

l

t

e

a

m

w

a

s

i

m

p

o

s

s

i

b

l

e

t

o

w

o

r

k

w

i

t

h

—

t

h

e

y

m

i

s

s

e

d

t

h

e

i

r

o

w

n

d

e

a

d

l

i

n

e

s

.

A

n

d

m

y

m

a

n

a

g

e

r

h

a

s

a

l

w

a

y

s

f

a

v

o

r

e

d

t

h

e

m

a

r

k

e

t

i

n

g

s

i

d

e

.

”

T

h

e

e

m

o

t

i

o

n

a

l

t

o

n

e

i

s

i

n

d

i

g

n

a

t

i

o

n

(

A

m

a

r

s

h

a

)

,

b

u

t

y

o

u

l

a

b

e

l

i

t

a

s

“

s

t

a

n

d

i

n

g

u

p

f

o

r

f

a

i

r

n

e

s

s

.

”

T

h

e

b

o

d

y

t

i

g

h

t

e

n

s

:

f

i

s

t

s

c

l

e

n

c

h

u

n

d

e

r

t

h

e

d

e

s

k

,

t

h

e

j

a

w

l

o

c

k

s

.

T

h

e

r

e

i

s

a

s

p

e

c

i

f

i

c

h

e

a

t

b

e

h

i

n

d

t

h

e

s

t

e

r

n

u

m

—

t

h

e

s

o

m

a

t

i

c

s

i

g

n

a

t

u

r

e

o

f

b

l

a

m

e

b

e

i

n

g

f

o

r

g

e

d

.

T

h

e

c

o

g

n

i

t

i

v

e

m

a

p

n

a

r

r

o

w

s

t

o

a

s

i

n

g

l

e

t

r

a

c

k

:

i

d

e

n

t

i

f

y

i

n

g

e

v

e

r

y

e

x

t

e

r

n

a

l

f

a

c

t

o

r

t

h

a

t

e

x

p

l

a

i

n

s

t

h

e

n

e

g

a

t

i

v

e

f

e

e

d

b

a

c

k

w

h

i

l

e

d

i

s

c

o

u

n

t

i

n

g

a

n

y

i

n

t

e

r

n

a

l

c

o

n

t

r

i

b

u

t

i

o

n

.

C

o

n

d

u

c

t

(

A

g

a

m

i

K

a

r

m

a

)

:

Y

o

u

s

p

e

n

d

t

h

e

e

v

e

n

i

n

g

c

o

m

p

o

s

i

n

g

a

r

e

b

u

t

t

a

l

e

m

a

i

l

c

a

t

a

l

o

g

i

n

g

e

v

e

r

y

i

n

s

t

a

n

c

e

o

f

t

h

e

c

r

o

s

s

-

f

u

n

c

t

i

o

n

a

l

t

e

a

m

’

s

f

a

i

l

u

r

e

s

.

Y

o

u

c

a

l

l

a

t

r

u

s

t

e

d

c

o

l

l

e

a

g

u

e

t

o

v

e

n

t

,

f

r

a

m

i

n

g

t

h

e

c

o

n

v

e

r

s

a

t

i

o

n

t

o

c

o

n

f

i

r

m

y

o

u

r

i

n

t

e

r

p

r

e

t

a

t

i

o

n

.

Y

o

u

b

e

g

i

n

s

u

b

t

l

y

d

i

s

t

a

n

c

i

n

g

y

o

u

r

s

e

l

f

f

r

o

m

t

h

e

p

e

e

r

s

w

h

o

g

a

v

e

t

h

e

c

r

i

t

i

c

a

l

f

e

e

d

b

a

c

k

,

r

e

d

u

c

i

n

g

c

o

l

l

a

b

o

r

a

t

i

o

n

f

u

r

t

h

e

r

.

T

h

e

n

e

x

t

m

o

r

n

i

n

g

,

y

o

u

a

r

r

i

v

e

a

t

w

o

r

k

w

i

t

h

a

“

p

r

o

t

e

c

t

i

v

e

”

p

o

s

t

u

r

e

—

p

o

l

i

t

e

b

u

t

a

r

m

o

r

e

d

,

e

n

g

a

g

i

n

g

o

n

l

y

w

h

e

r

e

n

e

c

e

s

s

a

r

y

,

g

i

v

i

n

g

n

o

o

n

e

n

e

w

a

m

m

u

n

i

t

i

o

n

.

O

u

t

c

o

m

e

(

S

a

ṃ

s

k

ā

r

a

R

e

i

n

f

o

r

c

e

m

e

n

t

)

:

T

h

e

r

e

b

u

t

t

a

l

e

m

a

i

l

,

w

h

e

t

h

e

r

s

e

n

t

o

r

n

o

t

,

h

a

s

a

l

r

e

a

d

y

d

e

e

p

e

n

e

d

t

h

e

g

r

o

o

v

e

.

T

h

e

S

a

ṃ

s

k

ā

r

a

o

f

e

x

t

e

r

n

a

l

i

z

e

d

b

l

a

m

e

—

t

h

e

a

u

t

o

m

a

t

i

c

p

a

t

t

e

r

n

o

f

s

e

a

r

c

h

i

n

g

f

o

r

t

h

e

e

n

v

i

r

o

n

m

e

n

t

a

l

c

a

u

s

e

o

f

e

v

e

r

y

d

i

s

c

o

m

f

o

r

t

—

b

e

c

o

m

e

s

m

o

r

e

e

n

t

r

e

n

c

h

e

d

.

T

h

e

n

e

x

t

t

i

m

e

f

e

e

d

b

a

c

k

a

r

r

i

v

e

s

,

t

h

e

d

e

f

e

n

s

i

v

e

a

r

c

h

i

t

e

c

t

u

r

e

w

i

l

l

a

c

t

i

v

a

t

e

f

a

s

t

e

r

a

n

d

m

o

r

e

r

i

g

i

d

l

y

.

T

h

e

L

o

k

e

s

h

a

n

a

(

c

r

a

v

i

n

g

f

o

r

s

t

a

t

u

s

)

t

h

a

t

d

r

o

v

e

t

h

e

i

n

i

t

i

a

l

r

e

a

c

t

i

o

n

r

e

m

a

i

n

s

u

n

e

x

a

m

i

n

e

d

,

e

n

s

u

r

i

n

g

t

h

a

t

p

r

o

f

e

s

s

i

o

n

a

l

i

d

e

n

t

i

t

y

c

o

n

t

i

n

u

e

s

t

o

b

e

t

h

e

f

r

a

g

i

l

e

o

u

t

e

r

w

a

l

l

r

a

t

h

e

r

t

h

a

n

t

h

e

s

t

a

b

l

e

i

n

n

e

r

f

l

o

o

r

.

I

n

t

e

r

n

a

l

L

a

n

d

s

c

a

p

e

:

T

h

e

s

a

m

e

i

n

d

i

g

n

a

t

i

o

n

a

r

i

s

e

s

—

t

h

e

h

o

t

f

l

a

s

h

b

e

h

i

n

d

t

h

e

s

t

e

r

n

u

m

,

t

h

e

j

a

w

t

i

g

h

t

e

n

i

n

g

.

B

u

t

i

n

s

t

e

a

d

o

f

i

m

m

e

d

i

a

t

e

l

y

r

o

u

t

i

n

g

t

h

e

e

n

e

r

g

y

o

u

t

w

a

r

d

,

y

o

u

p

a

u

s

e

.

Y

o

u

r

e

c

o

g

n

i

z

e

t

h

e

f

a

m

i

l

i

a

r

p

a

t

t

e

r

n

:

t

h

e

A

d

h

i

b

h

a

u

t

i

k

a

r

e

f

l

e

x

t

o

l

o

c

a

t

e

t

h

e

c

a

u

s

e

“

o

u

t

t

h

e

r

e

.

”

Y

o

u

n

a

m

e

i

t

:

“

T

h

i

s

i

s

m

y

L

o

k

a

-

v

ā

s

a

n

ā

—

m

y

p

r

o

f

e

s

s

i

o

n

a

l

i

d

e

n

t

i

t

y

f

e

e

l

s

t

h

r

e

a

t

e

n

e

d

,

a

n

d

m

y

f

i

r

s

t

i

n

s

t

i

n

c

t

i

s

t

o

f

i

n

d

s

o

m

e

o

n

e

e

l

s

e

t

o

b

l

a

m

e

.

”

T

h

e

i

n

d

i

g

n

a

t

i

o

n

d

o

e

s

n

’

t

v

a

n

i

s

h

—

i

t

i

s

s

t

i

l

l

p

h

y

s

i

c

a

l

l

y

p

r

e

s

e

n

t

i

n

t

h

e

c

h

e

s

t

—

b

u

t

i

t

i

s

n

o

w

a

n

o

b

s

e

r

v

e

d

p

h

e

n

o

m

e

n

o

n

r

a

t

h

e

r

t

h

a

n

a

d

i

r

e

c

t

i

v

e

.

Y

o

u

n

o

t

i

c

e

,

u

n

d

e

r

n

e

a

t

h

t

h

e

b

l

a

m

e

,

a

q

u

i

e

t

e

r

f

e

e

l

i

n

g

:

v

u

l

n

e

r

a

b

i

l

i

t

y

.

T

h

e

f

e

e

d

b

a

c

k

t

o

u

c

h

e

s

s

o

m

e

t

h

i

n

g

r

e

a

l

.

C

o

n

d

u

c

t

(

P

i

v

o

t

t

o

w

a

r

d

E

n

g

a

g

e

m

e

n

t

)

:

I

n

s

t

e

a

d

o

f

c

o

m

p

o

s

i

n

g

a

r

e

b

u

t

t

a

l

,

y

o

u

w

r

i

t

e

y

o

u

r

s

e

l

f

a

p

r

i

v

a

t

e

n

o

t

e

:

“

W

h

a

t

w

o

u

l

d

b

e

t

r

u

e

i

f

t

h

e

f

e

e

d

b

a

c

k

w

e

r

e

3

0

%

a

c

c

u

r

a

t

e

?

”

Y

o

u

i

d

e

n

t

i

f

y

o

n

e

s

p

e

c

i

f

i

c

c

o

l

l

a

b

o

r

a

t

i

o

n

f

a

i

l

u

r

e

w

h

e

r

e

y

o

u

r

o

w

n

r

i

g

i

d

i

t

y

p

l

a

y

e

d

a

r

o

l

e

.

T

h

e

n

e

x

t

d

a

y

,

y

o

u

a

p

p

r

o

a

c

h

a

p

e

e

r

f

r

o

m

t

h

e

c

r

o

s

s

-

f

u

n

c

t

i

o

n

a

l

t

e

a

m

a

n

d

a

s

k

a

g

e

n

u

i

n

e

q

u

e

s

t

i

o

n

a

b

o

u

t

h

o

w

y

o

u

r

w

o

r

k

i

n

g

s

t

y

l

e

a

f

f

e

c

t

e

d

t

h

e

i

r

e

x

p

e

r

i

e

n

c

e

.

T

h

i

s

i

s

a

K

a

r

m

a

Y

o

g

a

p

i

v

o

t

—

a

c

t

i

o

n

p

e

r

f

o

r

m

e

d

f

o

r

t

h

e

s

a

k

e

o

f

t

r

u

t

h

r

a

t

h

e

r

t

h

a

n

f

o

r

t

h

e

s

a

k

e

o

f

i

m

a

g

e

.

O

u

t

c

o

m

e

(

S

a

ṃ

s

k

ā

r

a

E

x

h

a

u

s

t

i

o

n

)

:

T

h

e

o

l

d

g

r

o

o

v

e

o

f

e

x

t

e

r

n

a

l

i

z

e

d

b

l

a

m

e

d

o

e

s

n

o

t

r

e

c

e

i

v

e

i

t

s

r

e

i

n

f

o

r

c

i

n

g

a

c

t

i

o

n

.

T

h

e

L

o

k

e

s

h

a

n

a

s

t

i

l

l

h

u

m

s

i

n

t

h

e

b

a

c

k

g

r

o

u

n

d

,

b

u

t

b

y

r

e

f

u

s

i

n

g

t

o

f

e

e

d

i

t

w

i

t

h

a

d

e

f

e

n

s

i

v

e

p

e

r

f

o

r

m

a

n

c

e

,

i

t

s

g

r

i

p

l

o

o

s

e

n

s

f

r

a

c

t

i

o

n

a

l

l

y

.

A

n

e

w

,

l

i

g

h

t

e

r

i

m

p

r

e

s

s

i

o

n

b

e

g

i

n

s

t

o

f

o

r

m

:

t

h

e

S

a

ṃ

s

k

ā

r

a

o

f

h

o

n

e

s

t

s

e

l

f

-

e

x

a

m

i

n

a

t

i

o

n

.

T

h

e

n

e

x

t

t

i

m

e

f

e

e

d

b

a

c

k

a

r

r

i

v

e

s

,

t

h

e

p

a

u

s

e

b

e

f

o

r

e

r

e

a

c

t

i

v

i

t

y

w

i

l

l

b

e

a

l

i

t

t

l

e

l

o

n

g

e

r

,

t

h

e

v

u

l

n

e

r

a

b

i

l

i

t

y

a

l

i

t

t

l

e

m

o

r

e

a

c

c

e

s

s

i

b

l

e

,

t

h

e

f

o

r

t

r

e

s

s

w

a

l

l

s

a

l

i

t

t

l

e

l

e

s

s

n

e

c

e

s

s

a

r

y

.', 1),
    (17, 'the_adhidaivika_perspective', 'The Adhidaivika Perspective', NULL, '“Life is a Cosmic Dialogue”', 'etad-yoniāni bhūtāni sarvāṇīty upadhāraya

ahaṃ kṛtsnasya jagataḥ prabhavaḥ pralayas tathā

Know that all beings have their origin in Me; I am the source of creation and dissolution — Bhagavad Gītā VII.6

The Adhidaivika lens relocates the center of gravity from the visible, tangible world to the vast, unseen architecture of cosmic forces. Through this perspective, the individual experiences themselves as a participant in a grand design—a small but meaningful thread in a tapestry woven by forces that vastly exceed human control or comprehension. Nothing is random. The sudden rainstorm, the chance encounter, the global crisis—each is read as a message or a mandate from a higher order, whether that order is conceived as Karma, divine will, the rhythm of the Yugas, or the impersonal laws of Ṛta (cosmic order).

Where the Adhibhautika person asks “Who did this to me?” the Adhidaivika person asks “Why is this happening now?”—and the “why” is always cosmic, never merely causal. The Ṛg Veda’s declaration—“The earth is His body, and the universe His manifestation”—captures the Adhidaivika experience at its most luminous: a world that is not a collection of objects but a living expression of divine intelligence.

T

h

e

s

c

e

n

a

r

i

o

:

Y

o

u

h

a

v

e

j

u

s

t

b

e

e

n

l

a

i

d

o

f

f

f

r

o

m

a

c

o

m

p

a

n

y

w

h

e

r

e

y

o

u

w

o

r

k

e

d

f

o

r

e

i

g

h

t

y

e

a

r

s

.

T

h

e

l

a

y

o

f

f

i

s

p

a

r

t

o

f

a

l

a

r

g

e

r

r

e

s

t

r

u

c

t

u

r

i

n

g

;

i

t

i

s

n

o

t

p

e

r

s

o

n

a

l

,

b

u

t

i

t

f

e

e

l

s

p

e

r

s

o

n

a

l

.

Y

o

u

a

r

e

f

i

f

t

y

-

o

n

e

y

e

a

r

s

o

l

d

.

I

n

t

e

r

n

a

l

L

a

n

d

s

c

a

p

e

:

T

h

e

A

d

h

i

d

a

i

v

i

k

a

e

x

c

e

s

s

a

c

t

i

v

a

t

e

s

a

s

a

p

r

o

t

e

c

t

i

v

e

s

h

i

e

l

d

.

W

i

t

h

i

n

h

o

u

r

s

o

f

t

h

e

n

e

w

s

,

y

o

u

h

a

v

e

r

e

f

r

a

m

e

d

t

h

e

e

n

t

i

r

e

e

v

e

n

t

i

n

c

o

s

m

i

c

t

e

r

m

s

:

“

T

h

e

u

n

i

v

e

r

s

e

i

s

c

l

e

a

r

i

n

g

t

h

e

p

a

t

h

f

o

r

s

o

m

e

t

h

i

n

g

b

i

g

g

e

r

.

T

h

i

s

w

a

s

m

e

a

n

t

t

o

h

a

p

p

e

n

.

”

T

h

e

b

o

d

y

s

o

f

t

e

n

s

i

n

t

o

a

p

r

e

m

a

t

u

r

e

p

e

a

c

e

—

t

h

e

m

u

s

c

l

e

s

r

e

l

e

a

s

e

n

o

t

b

e

c

a

u

s

e

y

o

u

h

a

v

e

p

r

o

c

e

s

s

e

d

t

h

e

s

h

o

c

k

b

u

t

b

e

c

a

u

s

e

t

h

e

c

o

s

m

i

c

n

a

r

r

a

t

i

v

e

h

a

s

s

h

o

r

t

-

c

i

r

c

u

i

t

e

d

t

h

e

n

e

e

d

t

o

f

e

e

l

i

t

.

U

n

d

e

r

n

e

a

t

h

t

h

i

s

s

p

i

r

i

t

u

a

l

c

o

m

p

o

s

u

r

e

,

t

h

e

r

e

i

s

a

t

r

e

m

o

r

o

f

f

e

a

r

(

T

r

ā

s

a

)

t

h

a

t

y

o

u

r

e

f

u

s

e

t

o

a

c

k

n

o

w

l

e

d

g

e

,

b

e

c

a

u

s

e

f

e

a

r

w

o

u

l

d

c

o

n

t

r

a

d

i

c

t

t

h

e

s

t

o

r

y

o

f

d

i

v

i

n

e

o

r

c

h

e

s

t

r

a

t

i

o

n

.

Y

o

u

m

i

s

l

a

b

e

l

t

h

e

f

e

a

r

a

s

“

e

x

c

i

t

e

m

e

n

t

a

b

o

u

t

t

h

e

n

e

x

t

c

h

a

p

t

e

r

.

”

C

o

n

d

u

c

t

(

A

g

a

m

i

K

a

r

m

a

)

:

Y

o

u

d

e

c

l

i

n

e

t

o

u

p

d

a

t

e

y

o

u

r

r

e

s

u

m

e

f

o

r

t

h

r

e

e

w

e

e

k

s

,

t

e

l

l

i

n

g

f

r

i

e

n

d

s

y

o

u

a

r

e

“

w

a

i

t

i

n

g

f

o

r

c

l

a

r

i

t

y

”

a

b

o

u

t

w

h

a

t

t

h

e

u

n

i

v

e

r

s

e

w

a

n

t

s

n

e

x

t

.

Y

o

u

s

p

e

n

d

m

o

r

n

i

n

g

s

i

n

e

x

t

e

n

d

e

d

m

e

d

i

t

a

t

i

o

n

,

w

h

i

c

h

f

e

e

l

s

n

o

u

r

i

s

h

i

n

g

b

u

t

i

s

a

l

s

o

f

u

n

c

t

i

o

n

i

n

g

a

s

a

v

o

i

d

a

n

c

e

o

f

t

h

e

p

r

a

c

t

i

c

a

l

w

o

r

k

o

f

j

o

b

s

e

a

r

c

h

i

n

g

.

W

h

e

n

a

f

o

r

m

e

r

c

o

l

l

e

a

g

u

e

o

f

f

e

r

s

a

c

o

n

c

r

e

t

e

l

e

a

d

,

y

o

u

h

e

s

i

t

a

t

e

b

e

c

a

u

s

e

t

h

e

o

p

p

o

r

t

u

n

i

t

y

d

o

e

s

n

’

t

“

f

e

e

l

a

l

i

g

n

e

d

.

”

Y

o

u

b

e

g

i

n

c

o

n

s

u

l

t

i

n

g

a

n

a

s

t

r

o

l

o

g

e

r

a

b

o

u

t

o

p

t

i

m

a

l

t

i

m

i

n

g

f

o

r

y

o

u

r

n

e

x

t

m

o

v

e

.

O

u

t

c

o

m

e

(

S

a

ṃ

s

k

ā

r

a

R

e

i

n

f

o

r

c

e

m

e

n

t

)

:

T

h

e

S

a

ṃ

s

k

ā

r

a

o

f

s

p

i

r

i

t

u

a

l

b

y

p

a

s

s

d

e

e

p

e

n

s

.

T

h

e

p

a

t

t

e

r

n

o

f

u

s

i

n

g

t

h

e

c

o

s

m

i

c

n

a

r

r

a

t

i

v

e

t

o

a

v

o

i

d

u

n

c

o

m

f

o

r

t

a

b

l

e

e

m

o

t

i

o

n

s

a

n

d

p

r

a

c

t

i

c

a

l

r

e

s

p

o

n

s

i

b

i

l

i

t

i

e

s

b

e

c

o

m

e

s

m

o

r

e

e

n

t

r

e

n

c

h

e

d

.

E

a

c

h

w

e

e

k

o

f

i

n

a

c

t

i

o

n

i

s

j

u

s

t

i

f

i

e

d

b

y

i

n

c

r

e

a

s

i

n

g

l

y

e

l

a

b

o

r

a

t

e

i

n

t

e

r

p

r

e

t

i

v

e

f

r

a

m

e

w

o

r

k

s

.

T

h

e

A

d

h

i

d

a

i

v

i

k

a

l

e

n

s

,

w

h

i

c

h

i

n

e

q

u

i

l

i

b

r

i

u

m

p

r

o

v

i

d

e

s

g

e

n

u

i

n

e

r

e

s

i

l

i

e

n

c

e

,

h

a

s

b

e

c

o

m

e

a

v

e

l

v

e

t

c

a

g

e

—

c

o

m

f

o

r

t

a

b

l

e

,

m

e

a

n

i

n

g

f

u

l

-

s

e

e

m

i

n

g

,

a

n

d

p

r

o

f

o

u

n

d

l

y

d

i

s

e

m

p

o

w

e

r

i

n

g

.

T

h

e

J

i

v

e

s

h

a

n

a

(

c

r

a

v

i

n

g

f

o

r

s

e

l

f

-

p

r

e

s

e

r

v

a

t

i

o

n

)

t

h

a

t

l

i

e

s

b

e

n

e

a

t

h

t

h

e

s

p

i

r

i

t

u

a

l

c

o

m

p

o

s

u

r

e

r

e

m

a

i

n

s

u

n

e

x

a

m

i

n

e

d

,

a

n

d

t

h

e

f

e

a

r

o

f

i

r

r

e

l

e

v

a

n

c

e

a

t

f

i

f

t

y

-

o

n

e

c

o

n

t

i

n

u

e

s

t

o

o

p

e

r

a

t

e

f

r

o

m

t

h

e

s

h

a

d

o

w

s

.

I

n

t

e

r

n

a

l

L

a

n

d

s

c

a

p

e

:

T

h

e

s

a

m

e

c

o

s

m

i

c

r

e

f

l

e

x

a

r

i

s

e

s

—

t

h

e

i

m

m

e

d

i

a

t

e

u

r

g

e

t

o

i

n

t

e

r

p

r

e

t

t

h

e

l

a

y

o

f

f

a

s

“

m

e

a

n

t

t

o

b

e

.

”

B

u

t

y

o

u

c

a

t

c

h

i

t

.

Y

o

u

n

o

t

i

c

e

t

h

a

t

t

h

e

s

p

i

r

i

t

u

a

l

f

r

a

m

i

n

g

a

r

r

i

v

e

d

s

u

s

p

i

c

i

o

u

s

l

y

f

a

s

t

,

b

e

f

o

r

e

y

o

u

h

a

d

a

c

t

u

a

l

l

y

f

e

l

t

a

n

y

t

h

i

n

g

.

Y

o

u

n

a

m

e

t

h

e

p

a

t

t

e

r

n

:

“

T

h

i

s

i

s

m

y

A

d

h

i

d

a

i

v

i

k

a

b

y

p

a

s

s

—

I

a

m

r

e

a

c

h

i

n

g

f

o

r

a

c

o

s

m

i

c

s

t

o

r

y

b

e

c

a

u

s

e

I

a

m

a

f

r

a

i

d

t

o

f

e

e

l

t

h

e

g

r

i

e

f

a

n

d

t

h

e

f

e

a

r

.

”

Y

o

u

a

l

l

o

w

t

h

e

f

e

a

r

t

o

s

u

r

f

a

c

e

:

t

h

e

c

o

l

d

w

e

i

g

h

t

i

n

t

h

e

s

t

o

m

a

c

h

,

t

h

e

c

o

n

t

r

a

c

t

i

o

n

i

n

t

h

e

t

h

r

o

a

t

.

Y

o

u

s

i

t

w

i

t

h

i

t

w

i

t

h

o

u

t

i

n

t

e

r

p

r

e

t

i

n

g

i

t

,

w

i

t

h

o

u

t

r

u

s

h

i

n

g

t

o

g

i

v

e

i

t

m

e

a

n

i

n

g

.

T

h

e

g

r

i

e

f

a

r

r

i

v

e

s

n

e

x

t

—

n

o

t

c

o

s

m

i

c

g

r

i

e

f

,

b

u

t

t

h

e

s

p

e

c

i

f

i

c

,

h

u

m

a

n

g

r

i

e

f

o

f

l

o

s

i

n

g

a

r

o

l

e

y

o

u

c

a

r

e

d

a

b

o

u

t

,

a

t

e

a

m

y

o

u

v

a

l

u

e

d

,

a

d

a

i

l

y

r

h

y

t

h

m

t

h

a

t

g

a

v

e

y

o

u

r

l

i

f

e

s

t

r

u

c

t

u

r

e

.

C

o

n

d

u

c

t

(

P

i

v

o

t

t

o

w

a

r

d

E

n

g

a

g

e

m

e

n

t

)

:

Y

o

u

h

o

n

o

r

t

h

e

A

d

h

i

d

a

i

v

i

k

a

p

e

r

s

p

e

c

t

i

v

e

w

i

t

h

o

u

t

b

e

i

n

g

c

a

p

t

u

r

e

d

b

y

i

t

.

Y

o

u

a

c

k

n

o

w

l

e

d

g

e

t

h

a

t

l

a

r

g

e

r

f

o

r

c

e

s

a

r

e

a

t

w

o

r

k

—

r

e

s

t

r

u

c

t

u

r

i

n

g

s

a

r

e

n

o

t

p

e

r

s

o

n

a

l

—

w

h

i

l

e

a

l

s

o

t

a

k

i

n

g

f

u

l

l

A

d

h

i

b

h

a

u

t

i

k

a

r

e

s

p

o

n

s

i

b

i

l

i

t

y

f

o

r

y

o

u

r

p

r

a

c

t

i

c

a

l

s

i

t

u

a

t

i

o

n

.

Y

o

u

u

p

d

a

t

e

y

o

u

r

r

e

s

u

m

e

o

n

d

a

y

t

h

r

e

e

.

Y

o

u

c

a

l

l

t

h

e

c

o

l

l

e

a

g

u

e

w

i

t

h

t

h

e

l

e

a

d

.

Y

o

u

a

l

s

o

b

e

g

i

n

a

d

e

v

o

t

i

o

n

a

l

p

r

a

c

t

i

c

e

e

a

c

h

m

o

r

n

i

n

g

—

n

o

t

a

s

a

v

o

i

d

a

n

c

e

b

u

t

a

s

a

g

e

n

u

i

n

e

o

f

f

e

r

i

n

g

o

f

y

o

u

r

u

n

c

e

r

t

a

i

n

t

y

t

o

s

o

m

e

t

h

i

n

g

l

a

r

g

e

r

.

T

h

e

p

r

a

c

t

i

c

e

i

s

:

“

I

w

i

l

l

d

o

m

y

p

a

r

t

w

i

t

h

f

u

l

l

e

f

f

o

r

t

;

I

w

i

l

l

r

e

l

e

a

s

e

a

t

t

a

c

h

m

e

n

t

t

o

t

h

e

s

p

e

c

i

f

i

c

f

o

r

m

o

f

t

h

e

o

u

t

c

o

m

e

.

”

T

h

i

s

i

s

B

h

a

k

t

i

Y

o

g

a

i

n

i

t

s

a

u

t

h

e

n

t

i

c

f

o

r

m

.

O

u

t

c

o

m

e

(

S

a

ṃ

s

k

ā

r

a

E

x

h

a

u

s

t

i

o

n

)

:

T

h

e

o

l

d

p

a

t

t

e

r

n

o

f

s

p

i

r

i

t

u

a

l

b

y

p

a

s

s

d

o

e

s

n

o

t

r

e

c

e

i

v

e

i

t

s

r

e

i

n

f

o

r

c

i

n

g

a

c

t

i

o

n

.

B

y

a

l

l

o

w

i

n

g

y

o

u

r

s

e

l

f

t

o

f

e

e

l

t

h

e

f

e

a

r

a

n

d

t

h

e

g

r

i

e

f

b

e

f

o

r

e

r

e

a

c

h

i

n

g

f

o

r

t

h

e

c

o

s

m

i

c

n

a

r

r

a

t

i

v

e

,

y

o

u

w

e

a

k

e

n

t

h

e

S

a

ṃ

s

k

ā

r

a

o

f

a

v

o

i

d

a

n

c

e

.

A

n

e

w

i

m

p

r

e

s

s

i

o

n

f

o

r

m

s

:

t

h

e

c

a

p

a

c

i

t

y

t

o

h

o

l

d

b

o

t

h

t

r

u

s

t

i

n

a

l

a

r

g

e

r

o

r

d

e

r

a

n

d

p

r

a

c

t

i

c

a

l

r

e

s

p

o

n

s

i

b

i

l

i

t

y

f

o

r

y

o

u

r

o

w

n

l

i

f

e

s

i

m

u

l

t

a

n

e

o

u

s

l

y

.

T

h

e

A

d

h

i

d

a

i

v

i

k

a

l

e

n

s

,

r

a

t

h

e

r

t

h

a

n

c

o

l

l

a

p

s

i

n

g

i

n

t

o

f

a

t

a

l

i

s

m

,

i

n

t

e

g

r

a

t

e

s

w

i

t

h

t

h

e

A

d

h

i

b

h

a

u

t

i

k

a

:

e

f

f

o

r

t

a

n

d

s

u

r

r

e

n

d

e

r

c

o

e

x

i

s

t

.

T

h

e

J

i

v

e

s

h

a

n

a

d

o

e

s

n

o

t

d

i

s

a

p

p

e

a

r

,

b

u

t

i

t

s

g

r

i

p

l

o

o

s

e

n

s

b

e

c

a

u

s

e

y

o

u

f

a

c

e

d

i

t

d

i

r

e

c

t

l

y

r

a

t

h

e

r

t

h

a

n

h

i

d

i

n

g

i

t

b

e

h

i

n

d

a

s

p

i

r

i

t

u

a

l

s

c

r

e

e

n

.', 2),
    (17, 'the_adhyatmika_perspective', 'The Ādhyātmika Perspective', NULL, '“The World is a Mirror”', 'uddhared ātmanātmānaṃ nātmānam avasādayet

ātmaiva hy ātmano bandhur ātmaiva ripur ātmanaḥ

One must elevate oneself by one’s own mind; the self alone is the friend and the enemy of the self — Bhagavad Gītā VI.5

The Ādhyātmika lens represents the most radical reorientation of attention available to a human being. It turns the gaze entirely inward, past the material environment (Adhibhautika), past the cosmic forces (Adhidaivika), toward the witnessing consciousness itself. The Kaṭha Upaniṣad’s declaration—“The Self is neither born nor does it die”—is not a theological proposition for this person but a lived reference point. The world “out there” is understood as a reflection of the state of mind “in here.” The characteristic question is not “Who did this to me?” or “Why is this happening?” but “Who am I in this experience?”

This is the perspective of the yogi, the philosopher, and the mature contemplative—someone who has realized that a change in perspective is more powerful than a change in scenery. Where the Adhibhautika person seeks to own the world and the Adhidaivika person seeks to appease it, the Ādhyātmika person seeks to transcend identification with the world by mastering the instrument of perception itself: the mind.

T

h

e

s

c

e

n

a

r

i

o

:

Y

o

u

a

r

e

a

w

a

k

e

n

e

d

a

t

2

A

M

b

y

a

s

h

a

r

p

,

u

n

f

a

m

i

l

i

a

r

p

a

i

n

i

n

y

o

u

r

c

h

e

s

t

.

I

t

l

a

s

t

s

a

b

o

u

t

f

o

r

t

y

-

f

i

v

e

s

e

c

o

n

d

s

,

t

h

e

n

f

a

d

e

s

.

Y

o

u

a

r

e

a

l

o

n

e

i

n

t

h

e

h

o

u

s

e

.

Y

o

u

r

p

h

o

n

e

i

s

o

n

t

h

e

n

i

g

h

t

s

t

a

n

d

.

I

n

t

e

r

n

a

l

L

a

n

d

s

c

a

p

e

:

T

h

e

Ā

d

h

y

ā

t

m

i

k

a

e

x

c

e

s

s

a

c

t

i

v

a

t

e

s

i

m

m

e

d

i

a

t

e

l

y

—

b

u

t

i

n

i

t

s

d

i

s

t

o

r

t

e

d

f

o

r

m

.

B

e

f

o

r

e

t

h

e

p

a

i

n

h

a

s

f

u

l

l

y

s

u

b

s

i

d

e

d

,

t

h

e

m

i

n

d

h

a

s

a

l

r

e

a

d

y

i

n

t

r

o

j

e

c

t

e

d

i

t

:

“

T

h

i

s

i

s

a

r

i

s

i

n

g

i

n

c

o

n

s

c

i

o

u

s

n

e

s

s

.

W

h

a

t

i

n

m

y

i

n

n

e

r

s

t

a

t

e

i

s

t

h

i

s

p

a

i

n

r

e

f

l

e

c

t

i

n

g

?

”

Y

o

u

b

e

g

i

n

i

n

t

e

r

p

r

e

t

i

n

g

t

h

e

c

h

e

s

t

p

a

i

n

a

s

a

“

h

e

a

r

t

c

h

a

k

r

a

b

l

o

c

k

a

g

e

”

o

r

t

h

e

s

o

m

a

t

i

c

m

a

n

i

f

e

s

t

a

t

i

o

n

o

f

u

n

p

r

o

c

e

s

s

e

d

g

r

i

e

f

.

T

h

e

f

e

a

r

i

s

p

r

e

s

e

n

t

—

t

h

e

c

o

l

d

s

w

e

a

t

o

n

t

h

e

p

a

l

m

s

,

t

h

e

r

a

c

i

n

g

h

e

a

r

t

—

b

u

t

y

o

u

o

v

e

r

r

i

d

e

i

t

w

i

t

h

t

h

e

w

i

t

n

e

s

s

i

n

g

p

o

s

t

u

r

e

:

“

I

a

m

t

h

e

o

b

s

e

r

v

e

r

o

f

t

h

i

s

f

e

a

r

,

n

o

t

t

h

e

f

e

a

r

i

t

s

e

l

f

.

”

T

h

e

b

o

d

y

’

s

a

l

a

r

m

s

y

s

t

e

m

i

s

s

e

n

d

i

n

g

a

c

l

e

a

r

s

i

g

n

a

l

,

b

u

t

t

h

e

Ā

d

h

y

ā

t

m

i

k

a

b

y

p

a

s

s

i

s

r

e

f

r

a

m

i

n

g

t

h

e

s

i

g

n

a

l

a

s

m

e

t

a

p

h

o

r

i

c

a

l

b

e

f

o

r

e

t

h

e

l

i

t

e

r

a

l

m

e

a

n

i

n

g

h

a

s

b

e

e

n

a

d

d

r

e

s

s

e

d

.

T

h

e

J

i

v

e

s

h

a

n

a

(

s

e

l

f

-

p

r

e

s

e

r

v

a

t

i

o

n

i

n

s

t

i

n

c

t

)

i

s

a

c

t

i

v

e

b

u

t

y

o

u

m

i

s

l

a

b

e

l

i

t

a

s

“

e

g

o

c

l

i

n

g

i

n

g

.

”

C

o

n

d

u

c

t

(

A

g

a

m

i

K

a

r

m

a

)

:

I

n

s

t

e

a

d

o

f

c

a

l

l

i

n

g

a

m

e

d

i

c

a

l

h

e

l

p

l

i

n

e

o

r

g

o

i

n

g

t

o

t

h

e

e

m

e

r

g

e

n

c

y

r

o

o

m

,

y

o

u

s

i

t

u

p

i

n

b

e

d

a

n

d

b

e

g

i

n

a

b

r

e

a

t

h

i

n

g

p

r

a

c

t

i

c

e

t

o

“

r

e

l

e

a

s

e

t

h

e

b

l

o

c

k

a

g

e

.

”

Y

o

u

t

e

l

l

y

o

u

r

s

e

l

f

t

h

a

t

y

o

u

w

i

l

l

“

c

h

e

c

k

i

n

w

i

t

h

t

h

e

b

o

d

y

i

n

t

h

e

m

o

r

n

i

n

g

”

a

n

d

t

h

a

t

t

h

e

p

a

i

n

i

s

“

a

t

e

a

c

h

e

r

,

n

o

t

a

t

h

r

e

a

t

.

”

Y

o

u

s

p

e

n

d

t

w

e

n

t

y

m

i

n

u

t

e

s

i

n

p

r

a

n

a

y

a

m

a

,

f

e

e

l

s

l

i

g

h

t

l

y

c

a

l

m

e

r

,

a

n

d

g

o

b

a

c

k

t

o

s

l

e

e

p

.

T

h

e

n

e

x

t

d

a

y

,

y

o

u

m

e

n

t

i

o

n

i

t

c

a

s

u

a

l

l

y

t

o

a

f

r

i

e

n

d

a

s

a

“

p

o

w

e

r

f

u

l

s

o

m

a

t

i

c

e

x

p

e

r

i

e

n

c

e

”

b

u

t

d

o

n

o

t

s

c

h

e

d

u

l

e

a

m

e

d

i

c

a

l

a

p

p

o

i

n

t

m

e

n

t

.

O

u

t

c

o

m

e

(

S

a

ṃ

s

k

ā

r

a

R

e

i

n

f

o

r

c

e

m

e

n

t

)

:

T

h

e

S

a

ṃ

s

k

ā

r

a

o

f

s

p

i

r

i

t

u

a

l

b

y

p

a

s

s

d

e

e

p

e

n

s

i

t

s

s

p

e

c

i

f

i

c

Ā

d

h

y

ā

t

m

i

k

a

g

r

o

o

v

e

:

t

h

e

p

a

t

t

e

r

n

o

f

o

v

e

r

r

i

d

i

n

g

t

h

e

b

o

d

y

’

s

a

l

a

r

m

s

i

g

n

a

l

s

w

i

t

h

c

o

n

t

e

m

p

l

a

t

i

v

e

r

e

f

r

a

m

i

n

g

.

T

h

e

A

d

h

i

b

h

a

u

t

i

k

a

d

i

m

e

n

s

i

o

n

—

t

h

e

s

i

m

p

l

e

,

p

r

a

c

t

i

c

a

l

f

a

c

t

t

h

a

t

c

h

e

s

t

p

a

i

n

i

n

t

h

e

m

i

d

d

l

e

o

f

t

h

e

n

i

g

h

t

r

e

q

u

i

r

e

s

m

e

d

i

c

a

l

e

v

a

l

u

a

t

i

o

n

—

h

a

s

b

e

e

n

s

u

p

p

r

e

s

s

e

d

b

y

t

h

e

d

o

m

i

n

a

n

t

i

n

n

e

r

l

e

n

s

.

I

f

t

h

e

p

a

i

n

h

a

s

a

b

e

n

i

g

n

e

x

p

l

a

n

a

t

i

o

n

,

y

o

u

h

a

v

e

b

e

e

n

l

u

c

k

y

.

I

f

i

t

d

o

e

s

n

o

t

,

y

o

u

h

a

v

e

t

r

a

d

e

d

a

t

r

e

a

t

a

b

l

e

c

o

n

d

i

t

i

o

n

f

o

r

a

b

e

a

u

t

i

f

u

l

i

n

t

e

r

p

r

e

t

a

t

i

o

n

.

T

h

e

J

i

v

e

s

h

a

n

a

w

a

s

n

o

t

t

r

a

n

s

c

e

n

d

e

d

;

i

t

w

a

s

d

e

n

i

e

d

.

I

n

t

e

r

n

a

l

L

a

n

d

s

c

a

p

e

:

T

h

e

s

a

m

e

w

i

t

n

e

s

s

i

n

g

c

a

p

a

c

i

t

y

a

c

t

i

v

a

t

e

s

,

b

u

t

t

h

i

s

t

i

m

e

i

t

i

s

h

o

n

e

s

t

.

Y

o

u

o

b

s

e

r

v

e

t

h

e

f

e

a

r

w

i

t

h

o

u

t

b

e

i

n

g

c

o

n

s

u

m

e

d

b

y

i

t

,

a

n

d

y

o

u

o

b

s

e

r

v

e

t

h

e

i

m

p

u

l

s

e

t

o

i

n

t

e

r

p

r

e

t

t

h

e

p

a

i

n

s

p

i

r

i

t

u

a

l

l

y

w

i

t

h

o

u

t

a

c

t

i

n

g

o

n

i

t

.

Y

o

u

n

a

m

e

t

h

e

p

a

t

t

e

r

n

:

“

T

h

i

s

i

s

m

y

Ā

d

h

y

ā

t

m

i

k

a

h

a

b

i

t

—

I

a

m

t

r

y

i

n

g

t

o

t

u

r

n

a

p

h

y

s

i

c

a

l

s

y

m

p

t

o

m

i

n

t

o

a

c

o

n

t

e

m

p

l

a

t

i

v

e

e

x

e

r

c

i

s

e

b

e

c

a

u

s

e

t

h

e

a

l

t

e

r

n

a

t

i

v

e

—

t

h

a

t

s

o

m

e

t

h

i

n

g

m

i

g

h

t

b

e

m

e

d

i

c

a

l

l

y

w

r

o

n

g

—

i

s

f

r

i

g

h

t

e

n

i

n

g

.

”

T

h

e

w

i

t

n

e

s

s

i

n

g

d

o

e

s

n

o

t

s

u

p

p

r

e

s

s

t

h

e

J

i

v

e

s

h

a

n

a

;

i

t

s

e

e

s

t

h

r

o

u

g

h

t

h

e

J

i

v

e

s

h

a

n

a

’

s

t

w

o

p

o

s

s

i

b

l

e

e

x

p

r

e

s

s

i

o

n

s

:

t

h

e

A

d

h

i

b

h

a

u

t

i

k

a

p

a

n

i

c

t

h

a

t

w

o

u

l

d

s

e

n

d

y

o

u

i

n

t

o

h

y

p

e

r

v

e

n

t

i

l

a

t

i

n

g

t

e

r

r

o

r

,

a

n

d

t

h

e

Ā

d

h

y

ā

t

m

i

k

a

b

y

p

a

s

s

t

h

a

t

w

o

u

l

d

s

e

n

d

y

o

u

i

n

t

o

s

e

r

e

n

e

d

e

n

i

a

l

.

E

p

i

s

t

e

m

i

c

i

n

t

e

g

r

i

t

y

r

e

v

e

a

l

s

a

t

h

i

r

d

o

p

t

i

o

n

:

c

a

l

m

,

p

r

a

c

t

i

c

a

l

r

e

s

p

o

n

s

e

.

C

o

n

d

u

c

t

(

P

i

v

o

t

t

o

w

a

r

d

E

n

g

a

g

e

m

e

n

t

)

:

Y

o

u

c

a

l

l

t

h

e

m

e

d

i

c

a

l

h

e

l

p

l

i

n

e

.

Y

o

u

r

v

o

i

c

e

i

s

s

t

e

a

d

y

b

e

c

a

u

s

e

t

h

e

w

i

t

n

e

s

s

i

n

g

c

o

n

s

c

i

o

u

s

n

e

s

s

i

s

g

e

n

u

i

n

e

l

y

o

p

e

r

a

t

i

o

n

a

l

—

y

o

u

a

r

e

n

o

t

i

d

e

n

t

i

f

i

e

d

w

i

t

h

t

h

e

f

e

a

r

,

b

u

t

y

o

u

a

r

e

n

o

t

i

g

n

o

r

i

n

g

i

t

s

m

e

s

s

a

g

e

e

i

t

h

e

r

.

Y

o

u

d

e

s

c

r

i

b

e

t

h

e

s

y

m

p

t

o

m

s

c

l

e

a

r

l

y

a

n

d

f

o

l

l

o

w

t

h

e

n

u

r

s

e

’

s

i

n

s

t

r

u

c

t

i

o

n

s

.

T

h

e

Ā

d

h

y

ā

t

m

i

k

a

c

a

p

a

c

i

t

y

s

e

r

v

e

s

i

t

s

p

r

o

p

e

r

f

u

n

c

t

i

o

n

:

i

t

p

r

o

v

i

d

e

s

t

h

e

i

n

n

e

r

s

t

a

b

i

l

i

t

y

t

h

a

t

a

l

l

o

w

s

y

o

u

t

o

a

c

t

f

r

o

m

c

l

a

r

i

t

y

r

a

t

h

e

r

t

h

a

n

p

a

n

i

c

.

T

h

e

A

d

h

i

b

h

a

u

t

i

k

a

d

i

m

e

n

s

i

o

n

i

s

h

o

n

o

r

e

d

:

y

o

u

t

r

e

a

t

t

h

e

b

o

d

y

a

s

a

l

e

g

i

t

i

m

a

t

e

d

o

m

a

i

n

o

f

c

a

r

e

.

T

h

e

A

d

h

i

d

a

i

v

i

k

a

d

i

m

e

n

s

i

o

n

p

r

o

v

i

d

e

s

b

a

c

k

g

r

o

u

n

d

t

r

u

s

t

:

w

h

a

t

e

v

e

r

t

h

e

o

u

t

c

o

m

e

,

y

o

u

c

a

n

m

e

e

t

i

t

.

A

l

l

t

h

r

e

e

l

e

n

s

e

s

c

o

l

l

a

b

o

r

a

t

e

r

a

t

h

e

r

t

h

a

n

c

o

m

p

e

t

e

.

O

u

t

c

o

m

e

(

S

a

ṃ

s

k

ā

r

a

E

x

h

a

u

s

t

i

o

n

)

:

T

h

e

o

l

d

g

r

o

o

v

e

o

f

s

p

i

r

i

t

u

a

l

b

y

p

a

s

s

d

o

e

s

n

o

t

r

e

c

e

i

v

e

r

e

i

n

f

o

r

c

e

m

e

n

t

.

T

h

e

p

a

t

t

e

r

n

o

f

o

v

e

r

r

i

d

i

n

g

t

h

e

b

o

d

y

’

s

s

i

g

n

a

l

s

w

i

t

h

c

o

n

t

e

m

p

l

a

t

i

v

e

r

e

f

r

a

m

i

n

g

i

s

w

e

a

k

e

n

e

d

.

A

n

e

w

,

i

n

t

e

g

r

a

t

e

d

i

m

p

r

e

s

s

i

o

n

f

o

r

m

s

:

t

h

e

c

a

p

a

c

i

t

y

t

o

w

i

t

n

e

s

s

i

n

n

e

r

e

x

p

e

r

i

e

n

c

e

w

h

i

l

e

s

t

i

l

l

h

o

n

o

r

i

n

g

t

h

e

b

o

d

y

’

s

w

i

s

d

o

m

a

n

d

t

h

e

w

o

r

l

d

’

s

p

r

a

c

t

i

c

a

l

d

e

m

a

n

d

s

.

T

h

e

t

h

r

e

e

l

e

n

s

e

s

—

A

d

h

i

b

h

a

u

t

i

k

a

,

A

d

h

i

d

a

i

v

i

k

a

,

a

n

d

Ā

d

h

y

ā

t

m

i

k

a

—

o

p

e

r

a

t

e

i

n

c

o

n

c

e

r

t

.

T

h

i

s

i

s

t

h

e

l

i

v

e

d

m

e

a

n

i

n

g

o

f

t

h

e

t

r

i

p

l

e

Ś

ā

n

t

i

:

p

e

a

c

e

i

n

t

h

e

b

o

d

y

,

p

e

a

c

e

i

n

t

h

e

c

o

s

m

o

s

,

p

e

a

c

e

i

n

t

h

e

s

e

l

f

—

n

o

t

s

e

q

u

e

n

t

i

a

l

l

y

,

b

u

t

s

i

m

u

l

t

a

n

e

o

u

s

l

y

.', 3);

-- D17 pole descriptions (9 rows)
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In its balanced state, the Adhibhautika lens is not a limitation but a strength. It is the perspective of the competent householder—the person who takes practical responsibility for their environment, tends to the body with discipline, and engages honestly with other beings. The Bhagavad Gītā’s emphasis on svadharma—one’s own duty in the world—is, in part, an affirmation of this perspective. The body must be fed, the family must be sheltered, and the community requires participation. Without the Adhibhautika orientation functioning well, the other two lenses lack a foundation.

Inner Presence

At the soul level, the Adhibhautika equilibrium represents the lesson of engagement. The spirit is learning to participate fully in the material drama without losing itself in it. There is an implicit faith that the world is workable—that effort matters, that relationships can be built, that the body is a worthy instrument. This is the necessary foundation for any deeper spiritual work: one must learn to live well in the world before one can learn to see beyond it.

External Conduct

Work is approached with diligence and measured by results. Relationships are maintained through reciprocal care and clear communication. Daily habits reflect an orderly engagement with the material world: regular exercise, organized living spaces, attention to nutrition. The person is a reliable colleague, a present partner, and an active community member. They vote, they volunteer, they fix things that are broken.', 'The body hums with functional alertness. There is a grounded quality to physical experience—the weight of one’s feet on the floor, the satisfying fatigue after meaningful labor, the simple pleasure of a meal eaten with attention. The nervous system operates in a ventral vagal state: relaxed but engaged, ready to act without being reactive. Posture is upright without rigidity. Sleep comes easily because the day’s physical tasks have been completed with reasonable thoroughness.', 'The emotional tone is one of pragmatic contentment. There is satisfaction in competence—the quiet pleasure of a well-organized home, a balanced budget, a problem solved through practical effort. Relationships carry the warmth of reciprocity: “I care for you, and I trust you to care for me.” Fear is present but proportionate—a healthy vigilance about genuine physical risks without catastrophizing. The underlying drive is toward security and harmony, but it does not dominate consciousness.', 'Thoughts are practical, sequential, and reality-oriented. The mind moves naturally through causal chains: “If I complete this task, then this outcome follows.” There is a healthy respect for evidence and measurable results. Ethical reasoning operates through social contracts and observable consequences: actions are evaluated by their tangible impact on self and others. The person can plan, troubleshoot, and adapt to changing material conditions with flexibility.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 17 AND c.slug = 'the_adhibhautika_perspective';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the Adhibhautika lens becomes dominant to the exclusion of the other two perspectives, the competent householder morphs into the fortress builder—a person whose entire identity is tethered to the external environment and who experiences any disruption to that environment as an existential threat. The world narrows to a high-stakes game of acquisition, control, and defense.

Inner Presence

The soul is trapped in the lesson it was meant to learn. Instead of engaging the material world as a field of practice, the person has confused the field with the totality of existence. The spirit is effectively asleep—buried under layers of acquisition, social performance, and sensory pursuit. The Adhyatmic voice is muffled. The Adhidaivic sense of cosmic participation is entirely absent. The person has “no shock absorbers,” as the tradition describes it: without the inner stability of the Ādhyātmika or the cosmic perspective of the Adhidaivika, every external disruption hits the core self directly.

External Conduct

Work becomes an arena of relentless competition. Relationships are transactional, scored by what each party “brings to the table.” Consumer behavior is compulsive—the next purchase always promising the satisfaction the last one failed to deliver. The person changes jobs, partners, and cities when the environment stops producing the expected rewards, never asking whether the problem might be internal. Health becomes an obsession with metrics—steps counted, calories tracked, biomarkers optimized—while the deeper vitality of the organism declines.', 'The body is chronically braced. Jaw tension becomes a permanent fixture. The shoulders creep upward toward the ears as if anticipating a blow. Digestion is erratic because the sympathetic nervous system rarely fully disengages. There is a peculiar combination of physical vigor—the person may exercise aggressively, eat meticulously, pursue every longevity hack—and an underlying brittleness, as though the body has been optimized but not inhabited. Sleep is fitful, interrupted by mental rehearsals of the next day’s battles.', 'The emotional register oscillates between the high of material wins—the dopamine surge of a promotion, a compliment, a luxury purchase—and the devastating crash when the external world fails to cooperate. A canceled flight triggers genuine rage. A critical comment from a colleague lands like a physical assault. The underlying current is anxiety—the perpetual low-grade fear that the environment is about to betray them. Envy becomes corrosive: every other person’s success is experienced as a personal diminishment. Blame is externalized reflexively: “If my partner were more supportive, I wouldn’t feel this way.”', 'The mind becomes a relentless cost-benefit calculator. Every interaction is evaluated for its utility: “What can this person do for me? What is this situation costing me?” Ethical reasoning degrades into pure reciprocity: “I will be good to you only so that you are good to me.” When something goes wrong, the cognitive search is always directed outward for the responsible party. Introspection feels pointless—why examine your inner state when the problem is clearly that other person, that unfair system, that unreliable economy? The thought pattern is reactive, competitive, and exhausting.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 17 AND c.slug = 'the_adhibhautika_perspective';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the Adhibhautika lens is underdeveloped, the person floats through the material world without adequate purchase on it. They may be deeply spiritual (Adhyatmic excess) or profoundly attuned to cosmic patterns (Adhidaivic excess), but they cannot pay their bills, maintain their health, or sustain practical relationships.

Inner Presence

The soul’s lesson here is that transcendence without embodiment is incomplete. The spirit may be reaching toward higher states, but it is doing so by abandoning the ground floor rather than integrating it. In Vedantic terms, this is a misunderstanding of Māyā—confusing the teaching that the world is not ultimate with the claim that the world is irrelevant. True liberation includes, rather than excludes, competent engagement with the material dimension.

External Conduct

Finances are chaotic or dependent on others. Living spaces reflect neglect. Physical health deteriorates through inattention. Relationships suffer because the person cannot show up for the mundane requirements of intimacy: remembering appointments, sharing household labor, being physically present and engaged. The person may be a profound meditator but an unreliable friend.', 'The body feels vaguely foreign—an inconvenient vehicle that the person tolerates but does not inhabit. Posture may be collapsed or ungrounded. Physical needs are neglected: meals are skipped not out of discipline but out of disconnection. The person may develop unexplained somatic symptoms—the body protesting its abandonment through pain that has no clear medical origin.', 'There is a peculiar emotional thinness—an inability to be fully moved by the concrete realities of life. The loss of a friendship registers as a philosophical event rather than a felt wound. Physical pleasure is met with a subtle detachment, as though the person is watching themselves eat rather than tasting the food. The underlying current is a quiet helplessness in the face of practical demands, masked by a narrative of spiritual superiority.', 'Practical thinking atrophies. Causal reasoning becomes vague: “Things will work out somehow” replaces concrete planning. The person may be brilliant at abstract contemplation but incapable of reading a lease agreement. Material concerns are dismissed as “lower” or “unspiritual,” which is itself a failure of the tradition’s actual teaching—that the Annamaya Kośa is not a prison to escape but a foundation to honor.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 17 AND c.slug = 'the_adhibhautika_perspective';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In its balanced form, the Adhidaivika perspective provides a profound resilience and a natural humility. The person does not carry the burden of cosmic authorship. They engage with life honestly while holding a larger context that prevents success from inflating the ego and failure from crushing the spirit. This is the perspective of the devoted naturalist—someone who acts with full effort but releases attachment to results because they trust a larger intelligence at work.

Inner Presence

The soul is learning the lesson of surrender—not passive resignation but active trust. The spirit practices releasing the illusion of total control while maintaining full engagement with life. This is the devotional dimension of the Pañca Kośa: the Ānandamaya sheath experiencing itself not as an isolated unit of consciousness but as a wave in an infinite ocean. The spiritual practice here is iśvarapraṇidhāna—offering one’s actions to the divine, which Patañjali identifies as a direct path to samādhi.

External Conduct

Work is approached with full effort but released with grace. The person is the colleague who remains calm during a crisis because they genuinely believe that not everything depends on human agency alone. Relationships carry a quality of reverence—the partner is seen not merely as a social companion but as a cosmic mirror. Daily habits include some form of devotional or contemplative practice: prayer, nature walks, ritual observance, or simply the habit of pausing to notice beauty. They tend to be generous, not because of social obligation, but because they experience themselves as channels for a larger abundance.', 'The body carries a particular quality of softness—not weakness, but a relaxation of the chronic bracing that characterizes Adhibhautika excess. The breath tends toward fullness rather than shallow restriction. There is a felt sense of being “held” by something larger than one’s own effort—a somatic trust that manifests as ease in the belly and openness across the chest. The person is more attuned to natural rhythms: seasonal changes, the quality of light at different hours, the body’s own tidal patterns of energy and rest.', 'The dominant emotional tone is a blend of humility and wonder. Success produces gratitude rather than triumph: “I was blessed” rather than “I conquered.” Failure produces acceptance rather than shame: “The timing was not right” rather than “I am worthless.” The underlying drive is toward alignment with something larger than personal will—a kind of emotional “listening” for guidance rather than grasping for control. Awe is a frequent visitor: sunsets genuinely move this person, coincidences are registered with a quiet thrill, and there is an abiding sense that life is fundamentally mysterious and enchanted.', 'Thinking follows a synchronistic rather than strictly causal logic. Decisions incorporate intuition, pattern recognition, and a sensitivity to timing alongside rational analysis. The person waits for a “sense of peace” before committing to major choices rather than relying solely on cost-benefit calculations. The moral framework is rooted in cosmic debt and cosmic harmony (Ṛta): actions are evaluated not just by their social consequences but by their alignment with a larger order. If a door remains closed, the Adhidaivika mind does not try to force it open; it pivots to where the energy flows.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 17 AND c.slug = 'the_adhidaivika_perspective';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the Adhidaivika lens dominates to the exclusion of the others, the devoted naturalist becomes the fatalist passenger—a person who has surrendered not just their anxiety but also their agency. The cosmic perspective, pushed to its extreme, becomes a rationalization for passivity.

Inner Presence

The soul has mistaken surrender for abdication. The spiritual lesson of trust has been corrupted into the spiritual bypass of avoidance. By attributing everything to cosmic forces, the person has absolved themselves of the very responsibility that would catalyze their growth. The Ānandamaya sheath is not being accessed through genuine devotion but used as a refuge from the discomfort of embodied action. This is the “leaf in the wind” syndrome: beautiful in theory, irresponsible in practice.

External Conduct

Practical obligations accumulate unaddressed. Finances drift because managing money feels spiritually crass. Health declines because the body is “in God’s hands.” Relationships suffer because the person cannot show up for the difficult, non-transcendent work of compromise and accountability. They may be profound in prayer but absent at the parent-teacher conference. Careers stagnate because the person waits for the universe to open doors rather than learning to knock.', 'The body becomes curiously inert—not the heavy inertia of Tamasic collapse, but a lighter, almost ethereal disengagement from physical urgency. Muscles lose their readiness to act. The person may neglect physical health not out of depression but out of a genuine belief that bodily matters are secondary to cosmic will. There is sometimes a dissociative quality: the body is present, but the person’s sense of agency within it has dimmed, as though they are watching their life from a slight remove.', 'The emotional landscape flattens into a permanent equanimity that is actually numbness wearing a spiritual costume. When the “forces” seem aligned, there is a luminous sense of grace and belonging. But when events turn adverse, the person sinks into paralyzing fatalism—a quiet, resigned belief that effort is futile because destiny has already decided the outcome. The healthy humility of equilibrium curdles into helplessness. Joy becomes dependent on external “signs” rather than arising from inner stability.', 'Decision-making becomes hostage to divination. The person may consult astrologers, wait for synchronicities, or defer major life choices indefinitely because the “signs” are not yet clear. Rational analysis is dismissed as “lacking faith.” The thought pattern of “it is meant to be” becomes an all-purpose explanation that forecloses genuine inquiry. Moral reasoning becomes circular: bad outcomes are attributed to “past-life karma” in a way that removes any motivation to act differently in this life.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 17 AND c.slug = 'the_adhidaivika_perspective';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the Adhidaivika perspective is absent or underdeveloped, the person lives in a world stripped of mystery, meaning, and any sense of being part of something larger than their own biography. Life becomes purely mechanical—a sequence of events with causes and effects but no significance beyond the immediate.

Inner Presence

The soul’s lesson here is that the rational mind, for all its brilliance, cannot generate meaning—it can only analyze it. The Ānandamaya sheath is starved: the deepest layer of selfhood, which requires communion with something that exceeds individual understanding, remains dormant. The person may achieve great material success and intellectual mastery while experiencing a persistent, unnamed emptiness that no external accomplishment can fill.

External Conduct

Work is efficient but soulless. Relationships are maintained through duty and routine but lack the quality of wonder that makes intimacy luminous. Daily life is well-organized but uninspired. The person does not pray, does not pause before nature, does not feel the pull of the sacred. When others speak of faith, intuition, or destiny, the person feels a mixture of dismissal and envy—unable to participate in a dimension of experience they have never accessed.', 'The body operates as a machine—maintained efficiently but experienced without reverence. There is no felt sense of being “held” by anything; the person carries their own weight entirely, and the musculature reflects this: perpetually engaged, perpetually load-bearing. Nature is experienced as scenery rather than as a living interlocutor. The person may walk through a forest and register its beauty intellectually while feeling nothing in the chest.', 'The emotional range is functional but contracted. There is no awe, no sense of the numinous, no capacity to be genuinely moved by mystery. When the unexpected occurs—a startling coincidence, an inexplicable turn of fortune—the person dismisses it as statistical noise rather than feeling into its possible significance. There is a specific loneliness in this: the loneliness of living in a universe that is not “speaking” to you, that has no intelligence beyond what humans can build or measure.', 'Thinking is rigorously causal and allergic to anything that cannot be empirically verified. This produces excellent analytical capacity but a blindness to pattern, intuition, and the kind of knowing that operates below the threshold of reason. Moral reasoning becomes purely contractual: right and wrong are determined by social agreement, not by any cosmic standard. The absence of a larger framework means the person has no narrative structure for absorbing meaningless suffering—when tragedy strikes, they are left with nothing but the raw fact of pain.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 17 AND c.slug = 'the_adhidaivika_perspective';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'In its balanced form, the Ādhyātmika perspective produces the sthita-prajña described in the Bhagavad Gītā: the person of steady wisdom who is not shaken by pleasure or pain because their identity is anchored in the witnessing consciousness rather than in the content of experience. This is not detachment born of numbness but equanimity born of depth.

Inner Presence

The soul is in its element. The Ānandamaya Kośa is active—the deepest sheath of being is pulsing with the quiet bliss of self-recognition. This is what the Upaniṣads call Ātma-jnāna: the direct knowing of one’s own nature as consciousness itself, prior to any role, relationship, or circumstance. The spiritual practice here is not effort but presence—the quality of attention that Patañjali describes as citta-vṛtti-nirodhaḥ: the cessation of the fluctuations of the mind-field, revealing the seer in its own nature.

External Conduct

Actions are responsive rather than reactive. The person takes the same “sacred pause” in a boardroom as in a meditation hall. They are fully engaged in their work but not identified with the outcomes. Relationships are marked by a rare quality of non-possessive presence: the partner feels truly seen, not because of any technique, but because the Ādhyātmika person has the inner space to actually attend to another being without the interference of ego-agenda. Daily habits include sustained contemplative practice, but also a surprising engagement with the material world—because the balanced Ādhyātmika knows that the internal and external are not truly separate.', 'The body is experienced from the inside out—not as an object to be managed but as a living field of awareness. There is a particular quality of stillness in the physical frame: not the rigidity of suppression but the calm of a lake with no wind. Breath is naturally full and rhythmic. Heart rate variability tends to be high—the physiological signature of a nervous system that can flexibly respond without becoming dysregulated. The person inhabits their body fully while understanding that they are not limited to it.', 'Emotions arise and are met with the quality that the tradition calls sākṣī-bhāva—witness consciousness. Anger appears and is recognized as anger without the added layer of “I am an angry person.” Grief surfaces and is honored as a natural movement of the heart without the narrative of permanent loss. The underlying emotional tone is a quiet, causeless contentment (Ānanda)—not the happiness that depends on circumstances but the wellbeing that arises from simply being present. Compassion flows naturally because the boundary between self and other has thinned: the other’s suffering is felt as a variation within the same field of consciousness.', 'Thinking is “inside-out.” When faced with a decision, the first question is not “What will this produce?” (Adhibhautika) or “Is this aligned with cosmic timing?” (Adhidaivika) but “Will this keep my mind clear? Will this support my growth as a conscious being?” Moral reasoning is grounded in self-knowledge: harm is avoided not because of social contracts or cosmic debt but because the Ādhyātmika person directly perceives that harming another is harming their own peace. The mind operates with a “sacred pause” before action—a gap between stimulus and response where choice lives.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'balance'
 WHERE c.dimension_id = 17 AND c.slug = 'the_adhyatmika_perspective';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the Ādhyātmika lens dominates without the grounding of the Adhibhautika or the connecting warmth of the Adhidaivika, the witnessing architect becomes the ivory tower ascetic—a person who has retreated so deeply into interior consciousness that they have lost touch with the world and the beings in it.

Inner Presence

The soul has confused the map for the territory. The insight that consciousness is primary has been weaponized into a justification for disengagement. The Ānandamaya Kośa is being accessed, but partially—the bliss of self-recognition has been divorced from the compassion and engagement that would complete it. In the Bhagavad Gītā’s framework, this is Arjuna’s initial error: the desire to retreat from the battlefield in the name of spiritual purity, which Krishna corrects by teaching that true yoga is engagement performed with inner freedom.

External Conduct

The person withdraws from community, responsibilities, and relationships. They may live in deliberate simplicity that tips into neglect—not the simplicity of clarity but the simplicity of avoidance. Close relationships atrophy because the person is genuinely more interested in their internal landscape than in the needs of the people around them. When confronted with this pattern, they respond with a gentle, maddening equanimity: “I am responsible for my inner state; others are responsible for theirs.”', 'The body becomes a neglected instrument. The person may sit for hours in meditation while their posture deteriorates, their nutrition falters, and their cardiovascular fitness declines. There is a subtle dissociation: the body is acknowledged as “not the Self” in a way that justifies neglecting it. Pain may be ignored or transcended through willpower rather than addressed with practical care. The somatic experience is one of progressive thinning—as though the person is slowly evaporating from their own physicality.', 'Emotional life flattens into a premature equanimity that is actually a sophisticated form of suppression. The person has not transcended their emotions; they have learned to override them with witnessing consciousness before the emotions have been fully felt and processed. Grief is observed but not wept. Anger is noticed but never allowed to mobilize constructive action. The result is a peculiar emotional sterility—the person appears serene, but close relationships reveal a quality of unavailability, as though there is no one “home” behind the witnessing.', 'The mind becomes trapped in a hall of mirrors. Every external event is immediately introjected: “What does this reveal about my inner state?” While this is a powerful practice in moderation, in excess it becomes a way of avoiding engagement with the world’s genuine demands. When a community faces injustice, the Ādhyātmika excess responds with: “All suffering is created by the mind”—which, while containing a partial truth, functions as a refusal to act. The cognitive map shrinks to a solipsistic loop: everything is internal, nothing is truly “out there,” and therefore nothing external requires genuine response.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'excess'
 WHERE c.dimension_id = 17 AND c.slug = 'the_adhyatmika_perspective';
INSERT INTO svarupa_concept_descriptions
    (concept_id, status_id, description, physical, emotional, mental)
SELECT c.concept_id, s.status_id, 'When the Ādhyātmika perspective is absent, the person has no inner refuge—no capacity to step back from the content of their experience and observe it with any distance. They are completely identified with every thought, every emotion, every circumstance. There is no witness; there is only the weather.

Inner Presence

The soul’s deepest lesson is the one most urgently needed and most thoroughly avoided: the recognition that “I am not my thoughts, not my emotions, not my circumstances.” The Ānandamaya Kośa is dormant—the deepest layer of selfhood has never been contacted. The person lives entirely on the surface of consciousness, buffeted by every wave, with no access to the still depths below. The spiritual ache manifests as a persistent sense that something essential is missing, but the person searches for it in relationships, achievements, and experiences rather than in the mirror of their own awareness.

External Conduct

Life is reactive and exhausting. Decisions are made impulsively based on the strongest current emotion. Relationships are intense but unsustainable: the person brings their entire unprocessed emotional world into every interaction and is bewildered when others withdraw under the weight of it. Work performance fluctuates wildly based on mood. The person may accumulate coping mechanisms—substances, compulsive activity, constant social stimulation—all of which serve to prevent the terrifying moment of sitting alone with their own mind.', 'The body is a live wire of reactivity. Every external stimulus produces an immediate and unmodulated physical response. A critical email triggers a cortisol spike that takes hours to resolve. A compliment produces a giddy rush that equally destabilizes. The person has no “inner volume control”—they are at the mercy of whatever signal the environment sends. The nervous system oscillates between sympathetic overdrive and parasympathetic collapse with no stable middle ground.', 'Emotions are experienced as absolute truths rather than passing states. “I feel anxious” becomes “The world is threatening.” “I feel sad” becomes “Life is hopeless.” There is no space between the emotion and the identity: every feeling is a verdict. Relationships are turbulent because the person’s emotional state is entirely dependent on the other person’s behavior—a late reply becomes evidence of abandonment, a careless comment becomes a mortal wound. The underlying current is fear, but it has no name because the person has never had the internal distance to observe it as a pattern.', 'Thinking is captured by the most recent stimulus. There is no executive function overseeing the thought stream; thoughts arrive and are obeyed. The mind churns in reactive loops: rehearsing arguments, catastrophizing outcomes, replaying slights. Self-reflection is absent or superficial—the person may describe their problem in elaborate detail but never asks the deeper question: “Why does this affect me this way?” The assumption is always that the experience is caused entirely by external factors, because the internal dimension of causation is invisible to them.'
  FROM svarupa_concepts c
  JOIN svarupa_status   s ON s.code = 'deficiency'
 WHERE c.dimension_id = 17 AND c.slug = 'the_adhyatmika_perspective';

-- -----------------------------------------------------------------------------
-- D18 — Science of Cosmic Light  (9 concepts)
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, category, description, sort_order)
VALUES
    (18, 'surya', 'Sūrya', NULL, 'The Principle of Selfhood', '"Sūryo ātmā jagatas tasthuṣaś ca"

(The Sun is the soul of all that moves and all that is still.)

— Ṛgveda 1.115.1

Sūrya governs Ātma-tattva—the principle of the Self. In the body, it rules the heart, the spine, and overall vitality. In the psyche, it represents the will, self-confidence, authority, and the capacity to radiate one’s unique purpose into the world. Sūrya’s Daśā period is six years.

Equilibrium: The Healthy Solar Principle

Somatic Base (Annamaya):

The body feels warm, vital, and upright. There is a natural gravitational pull toward good posture—the spine elongates without effort, the chest is open, the gaze is direct. Digestion is strong (Sūrya governs Agni, the digestive fire). Energy peaks in mid-morning and sustains through the afternoon. Sleep is regular and restorative. One wakes without an alarm, feeling ready.

Emotional Current (Prāṇamaya):

There is a quiet, steady sense of self-worth that does not depend on external validation. Confidence arises naturally, without inflation or deflation. Relationships with authority figures—fathers, bosses, mentors—feel appropriately differentiated: respectful but not servile, self-assured but not combative. There is generosity of spirit, a willingness to illuminate and uplift others without feeling diminished.

Cognitive Map (Manomaya/Vijñānamaya):

Thinking is clear, purposeful, and decisive. One can set a goal and pursue it without constant second-guessing. The internal narrative is organized around a stable sense of identity: “I know who I am. I know what I am here to do.” There is a capacity for leadership—not through domination, but through clarity of vision that others naturally follow.

Inner Presence (Ānandamaya):

The soul experiences itself as a unique expression of the divine. There is a felt connection to one’s Svadharma—a sense of being aligned with one’s cosmic purpose. The ego serves as a transparent vehicle for the Ātman’s light rather than an opaque wall that blocks it.

Excess: Solar Inflation (“Too Much Sun”)

Somatic Base:

The body runs hot. There may be chronic inflammation, acid reflux, or skin conditions related to Pitta aggravation. Headaches concentrate around the crown and temples. The eyes feel strained, as though perpetually glaring. There is a wired, taut quality to the musculature—always bracing, never fully relaxing. Sleep becomes short and fitful; one wakes at 3 or 4 a.m. with the mind already racing.

Emotional Current:

Confidence curdles into arrogance. The need to be recognized becomes compulsive. There is a prickly defensiveness when authority is questioned—a flash of rage that feels disproportionate to the stimulus. Relationships become hierarchical rather than reciprocal: others are either above or below, never alongside. Criticism, no matter how constructive, feels like an existential threat. The father wound or the authority wound is activated and projected outward.

Cognitive Map:

Thinking becomes autocratic. “My way is the only way.” There is a dismissiveness toward alternative viewpoints, a tendency to assume one already knows the answer before the question has been fully asked. Planning becomes grandiose—the goals inflate beyond what is realistic, and failure to achieve them triggers not humility but fury. The inner monologue sounds like a king who has been insulted.

Inner Presence:

The ego has eclipsed the Ātman. The personality now mistakes itself for the soul. Spiritual practice, if present at all, serves the ego’s agenda—acquiring status as a “spiritual person” rather than genuine self-transcendence. The soul’s lesson at this stage is precisely the humiliation or defeat that the inflated ego most fears.

Deficiency: Solar Depletion (“Too Little Sun”)

Somatic Base:

Vitality is low. The body feels heavy, cold, and sluggish—as though the internal fire has dimmed. The spine curves forward; the posture collapses inward, as if protecting the heart from exposure. Chronic fatigue, weak digestion, and susceptibility to illness are common. The immune system underperforms. There is a pallor, a dullness to the skin and eyes.

Emotional Current:

Self-worth is fragile or absent. There is a persistent sense of invisibility—a feeling that one does not matter, that one’s contributions go unseen. The relationship with authority is either overly submissive (desperately seeking approval from father-figures) or completely avoidant (withdrawing from any situation that requires stepping into one’s own power). The emotional tone is a quiet, chronic shame.

Cognitive Map:

Thinking is indecisive and self-undermining. “Who am I to lead? Who am I to speak? Who am I to shine?” The internal narrative is dominated by imposter syndrome—a conviction that any success is accidental and will soon be exposed as fraud. Goals are set too low or not at all. There is a cognitive dimming, as though the light of clarity has been turned down.

Inner Presence:

The soul’s unique purpose is buried under layers of self-doubt and social conformity. The individual lives someone else’s life—following the expectations of family, culture, or institution—while their authentic vocation atrophies. The spiritual lesson here is the reclamation of one’s own light, the courage to stand in one’s Svadharma even when no one applauds.

Vignette: The Promotion Decision

Scenario A: The Binding Path (Low Epistemic Integrity)

Context: Raj, 42, is offered a promotion to department head. It requires him to present his vision to the entire leadership team—something he has never done.

Internal Landscape: Raj’s Sun is debilitated in his natal chart, and he is currently in a Solar sub-period. The moment the offer arrives, his stomach drops. A voice in his head whispers: “You’re not qualified. They’ll see through you.” But instead of recognizing this as Solar deficiency—a pattern of dimmed self-worth—he rationalizes it as pragmatism: “I’m not ambitious. I’m just realistic.”

Conduct (Agami Karma): Raj declines the promotion, citing “family obligations.” In the weeks that follow, he watches a less experienced colleague take the role. A slow, acidic resentment builds. He becomes passive-aggressive in meetings, offering sardonic comments that disguise bitterness as humour.

Outcome: The Saṃskāra of self-erasure deepens. The groove in his psyche that says “I am not meant to shine” hardens further. His Vāsanā of avoidance now extends beyond work into all domains: he stops initiating social plans, stops expressing opinions at family gatherings, stops suggesting vacation ideas. The Sun’s light retreats further inward, unexpressed.

Scenario B: The Liberating Path (High Epistemic Integrity)

Internal Landscape: Raj notices the stomach-drop, the cold contraction in his chest. He pauses. “There it is again—the old pattern. The shrinking.” He does not fight the feeling or rationalize it. He simply observes: “This is my debilitated Sun speaking. This is the karmic terrain I was born to traverse.”

Conduct (The Pivot): Raj accepts the promotion—not because the fear has disappeared, but because he recognizes the fear as the very curriculum he is meant to face. He begins a disciplined morning practice of Sūrya Namaskāra (Sun Salutations) and recites the Āditya Hṛdayam—a Vedic hymn to strengthen Solar energy. He asks a trusted mentor to coach him for the presentation. His preparation is thorough, rooted in humility rather than hubris (the Path of Karma).

Outcome: The Saṃskāra of self-erasure is met with conscious heat. Each time Raj stands before the leadership team and speaks his truth, the old groove weakens. The Eṣaṇā for invisibility—the deep craving to remain safely unseen—begins to loosen its grip. His Sun does not become exalted overnight; but it becomes functional. The light finds a channel.

✦  ✦  ✦', 1),
    (18, 'chandra', 'Chandra', NULL, 'The Principle of Mind and Emotional Life', '"Candramā manaso jātaḥ"

(The Moon was born from the cosmic Mind.)

— Puruṣa Sūkta, Ṛgveda 10.90.13

Chandra governs Manas—the mind as the organ of feeling, reception, and emotional processing. In the body, it rules the stomach, bodily fluids, the breasts, and the menstrual cycle. In the psyche, it represents emotional intelligence, nurturing capacity, the relationship with the mother and mothering, and the fundamental mood-tone through which one filters all experience. Roughly 60% of the human body is water; the Moon’s gravitational influence on terrestrial tides mirrors its pull on the internal ocean of feeling. Chandra’s Daśā period is ten years.

Equilibrium: The Healthy Lunar Principle

Somatic Base:

The body feels fluid and receptive. Digestion is smooth; sleep is deep and restorative. There is a sensitivity to bodily rhythms—hunger, thirst, fatigue are noticed and honoured rather than overridden. The face is relaxed, the eyes soft. There is a quality of receptivity in the muscles—a suppleness that allows the body to adapt to the changing demands of each day without stiffening.

Emotional Current:

Emotions flow like a clean river—arising, being felt, and passing without stagnation or flooding. There is a capacity to hold others’ emotions without absorbing them, to empathize without losing one’s own centre. Relationships feel nourishing; there is an instinctive sense for what the people around you need, and a capacity to provide it without self-depletion. The connection with the mother archetype is healthy—one can both receive care and offer it without transaction.

Cognitive Map:

The mind is receptive and intuitive. Solutions to problems arrive not only through analysis but through a felt sense—a “hunch” that proves reliable. Memory is vivid and emotionally textured. The internal narrative includes the language of feeling: “This feels right” sits comfortably alongside “The data supports this.” There is no war between logic and intuition.

Inner Presence:

The soul experiences the world through the lens of belonging. There is a felt sense of being held by something larger—a cosmic mother, a sustaining ground. This is not sentimentality; it is the authentic perception that consciousness is inherently relational, that the individual is never truly isolated.

Excess: Lunar Flooding (“Too Much Moon”)

Somatic Base:

The body retains water, swells, and feels heavy. Digestion becomes sluggish; there is a tendency toward excess mucus, congestion, and Kapha-type ailments. Sleep becomes excessive but unrefreshing—drowning in dreams that leave one feeling more exhausted upon waking. The skin may be pale and puffy. There is a physical clinging quality, as though the body itself does not want to let go.

Emotional Current:

Emotions become overwhelming and boundary-less. One is awash in feeling—not just one’s own, but everyone’s. Empathy becomes enmeshment. The emotional field is like a sponge that absorbs every ambient mood in the room. Mood swings become rapid and intense—elation at 10 a.m., despair by noon—driven by the slightest environmental trigger. The relationship with the mother becomes suffocating, either through over-identification or through angry rejection of what feels like emotional manipulation.

Cognitive Map:

Thinking becomes circular and emotion-driven. Decisions are made (and unmade) based on how one “feels in the moment,” which changes constantly. Rumination takes hold—the same emotional wound is replayed endlessly without resolution. The internal narrative is dominated by anxiety about abandonment: “What if they leave? What if no one cares? Am I lovable?” Logic is drowned out by the tidal surge of feeling.

Inner Presence:

The soul cannot distinguish its own needs from those projected upon it by others. Identity becomes a mirror—reflecting whatever the nearest person seems to want. Spiritual practice becomes another form of emotional seeking: attending to the comforting, the soothing, the warm, while avoiding the sharp, the confrontational, the illuminating. The lesson at this stage is discernment—learning where “I” end and “you” begin.

Deficiency: Lunar Drought (“Too Little Moon”)

Somatic Base:

The body feels dry, brittle, and tense. Skin cracks. Joints ache. Sleep is thin and easily disrupted. There is a Vata-quality depletion—as though the body’s internal moisture has evaporated. The stomach is irritable; comfort foods are either craved compulsively or rejected entirely. The face appears drawn, the eyes hard.

Emotional Current:

Emotions are suppressed, dissociated, or simply inaccessible. When asked “How do you feel?” the honest answer is: “I don’t know.” There is a flatness to the emotional landscape—neither joy nor grief fully registers. Relationships feel transactional rather than nourishing. The capacity to nurture is impaired: one may provide material support while being emotionally absent. The mother wound manifests as an inability to receive care—a flinch when tenderness is offered.

Cognitive Map:

Thinking becomes hyper-rational to the exclusion of intuition. The mind operates like a machine—efficient but cold. Decisions are made purely on data, and the felt dimension of experience is dismissed as “irrelevant” or “weak.” The internal narrative might sound like: “Feelings are a liability. Vulnerability is dangerous. I handle things myself.”

Inner Presence:

The soul experiences a fundamental disconnection from the ground of being. There is no felt sense of being held, nourished, or belonging. The spiritual practice, if any, is austere and cerebral—meditation pursued as a cognitive exercise rather than a softening into presence. The lesson is the recovery of the feminine, the receptive, the capacity to surrender control and allow oneself to be moved.

Vignette: The Late-Night Call from a Friend

Scenario A: The Binding Path (Low Epistemic Integrity)

Context: Meera, 35, receives a call at 11 p.m. from a friend in distress. This is the fourth such call this month. Meera’s Moon is strong but afflicted by Rahu, creating emotional boundary confusion.

Internal Landscape: Meera’s chest tightens the moment the phone rings. She knows this pattern. She is exhausted; she has a presentation at 8 a.m. But a wave of guilt rises: “What kind of friend hangs up on someone who’s suffering?” She misidentifies her depletion as selfishness. The Moon-Rahu conjunction tells her that absorbing someone else’s pain is the same as love.

Conduct: Meera stays on the phone for two hours, offering the same reassurances she offered last week. She cancels her alarm, oversleeps, and arrives at the presentation flustered and underprepared. She snaps at a colleague, then feels guilty about that too.

Outcome: The Saṃskāra of self-erasure-through-caregiving deepens. The boundary between Meera’s emotional life and her friend’s becomes further eroded. The Vāsanā of compulsive nurturing—an over-activated Moon—hardens into a fixed identity: “I am the one who is always there.” Underneath this identity, Meera’s own unfelt grief accumulates.

Scenario B: The Liberating Path (High Epistemic Integrity)

Internal Landscape: Meera feels the tightness, the guilt, the pull to rescue. She pauses. “This is the Moon-Rahu pattern. The boundary is dissolving. My exhaustion is real. My guilt is the Saṃskāra talking, not my conscience.”

Conduct: Meera answers, listens for ten minutes with genuine presence, and then says: “I love you, and I need to sleep so I can show up fully tomorrow. Can we talk after my presentation?” She hangs up, places her phone in another room, and does five minutes of Moon-strengthening prāṇāyāma (left-nostril breathing, activating the Īdā Nāḍī) before sleep.

Outcome: The Saṃskāra of boundaryless care is met with a moment of discernment. The Eṣaṇā for emotional fusion does not vanish, but each time Meera draws a loving boundary, the old groove weakens. Her Moon retains its warmth without losing its shape.

✦  ✦  ✦', 2),
    (18, 'mangala', 'Maṅgala', NULL, 'The Principle of Action and Will', 'Maṅgala governs the warrior energy—courage, assertion, physical vitality, and the capacity to fight for what matters. In the body, it rules the blood, muscles, adrenal system, and the immune response. In the psyche, it represents ambition, competitive drive, sexual energy, and the willingness to face conflict. Mars’s Daśā period is seven years.

Equilibrium: The Healthy Martial Principle

Somatic Base:

The body feels strong, responsive, and ready. Muscles are toned without being rigid. The immune system is robust. There is a clean, sharp quality to physical energy—the ability to sprint when needed, to lift when required, to recover quickly from exertion. Sexual energy is present and healthy, neither obsessive nor absent. The digestion is strong; there is a good appetite.

Emotional Current:

There is a clean anger available—the capacity to assert boundaries without cruelty. Frustration is felt, expressed, and released rather than suppressed or weaponized. Competitive drive is healthy: one can strive to win without needing to destroy the opponent. There is courage—a willingness to enter difficult conversations, to defend the vulnerable, to take risks when the cause is worthy.

Cognitive Map:

Thinking is decisive and action-oriented. Problems are approached as challenges to be overcome rather than mysteries to be endlessly pondered. The internal narrative is: “What needs to be done? I’ll do it.” There is strategic intelligence—the ability to assess a situation, identify the point of leverage, and act with precision.

Inner Presence:

The soul understands that right action (Dharma) sometimes requires confrontation. The Bhagavad Gītā’s central teaching—that Arjuna must fight, not out of hatred but out of alignment with his Svadharma—is the archetype of healthy Mars. The warrior serves the spirit, not the ego.

Excess: Martial Conflagration (“Too Much Mars”)

Somatic Base:

The body runs hot and acidic. Inflammation is chronic: skin eruptions, ulcers, headaches at the temples. The musculature is perpetually tense, ready for a fight that never quite arrives. Sleep is aggressive—too short, broken by adrenaline surges. Injuries are frequent, often from reckless physical activity. There is a fever-quality to the body—a burning that does not cool.

Emotional Current:

Anger becomes the default emotional register. The world is perceived through a lens of threat and competition. Even neutral encounters are scanned for potential challenge. Impatience escalates into rage at minor provocations—a slow driver, a delayed email, a child’s mess. Relationships become battlefields. Sexual energy becomes aggressive or compulsive, divorced from tenderness. There is a deep loneliness underneath the armour, but admitting it feels like defeat.

Cognitive Map:

Thinking becomes combative and zero-sum. “If you’re not with me, you’re against me.” Nuance disappears. Planning becomes tactical rather than strategic—focused on winning the immediate battle without considering the larger war. The internal monologue sounds like a drill sergeant: relentless, punishing, never satisfied.

Inner Presence:

The warrior has forgotten whom he serves. Action has become compulsive rather than purposeful. The ego’s need to dominate has eclipsed the soul’s call to serve. The spiritual lesson is surrender—not weakness, but the recognition that true strength includes the ability to put down the sword.

Deficiency: Martial Collapse (“Too Little Mars”)

Somatic Base:

The body feels weak and undefended. Muscles atrophy; the immune system falters. There is a susceptibility to infections, anemia, and chronic fatigue. Physical energy is low. Sexual vitality is diminished or inaccessible. The body language is collapsed and retreating—shoulders curved inward, gaze averted.

Emotional Current:

Anger is absent or inaccessible. Boundaries are nonexistent. The individual cannot say no, cannot confront, cannot assert a preference. Resentment builds silently underneath the surface of compliance, eventually erupting as passive-aggression or psychosomatic illness. There is a deep frustration at one’s own perceived weakness—a self-contempt for not being able to fight.

Cognitive Map:

Thinking is hesitant and avoidant. Decisions are deferred endlessly. The internal narrative: “I don’t want conflict. I’ll just let it go.” But “letting it go” is actually suppression, not release. The mind avoids direct confrontation with any problem, preferring circular rumination to decisive action.

Inner Presence:

The soul’s capacity for righteous action is dormant. The Arjuna who should be on the battlefield is instead sitting in the tent, paralyzed by doubt. The spiritual lesson is the recovery of agency—the recognition that non-action in the face of injustice is itself a form of violence.

Vignette: The Workplace Injustice

Scenario A: The Binding Path (Low Epistemic Integrity)

Context: Arun, 28, discovers his manager has taken credit for a project Arun designed. Arun’s Mars is debilitated in Cancer in the 10th house.

Internal Landscape: A wave of heat rises in Arun’s chest, but before it reaches his throat it is swallowed. His hands go cold. “Forget it. It’s not worth the fight. He’s the boss.” Arun relabels his anger as “acceptance” and his cowardice as “professionalism.”

Conduct: Arun says nothing. He smiles in the all-hands meeting when the manager is praised. That night he eats three servings of dessert and scrolls his phone until 2 a.m. The suppressed Mars energy channels into self-harm through neglect.

Outcome: The Saṃskāra of passive surrender deepens. Arun’s Vāsanā for self-erasure in the face of authority now extends to his relationship, where he cannot express needs. The debilitated Mars stores unexpressed fire in the body, manifesting over months as tension headaches and TMJ pain.

Scenario B: The Liberating Path (High Epistemic Integrity)

Internal Landscape: Arun notices the heat, the subsequent freezing, the impulse to swallow. “There’s the pattern—anger arises, then collapses into submission. That’s my debilitated Mars. The fire is there. It just needs a conscious channel.”

Conduct: Arun does not confront the manager impulsively. Instead, he begins a daily regimen of vigorous physical exercise (channelling Mars through the body) and prepares a clear, factual email to the manager requesting a meeting to discuss attribution. His tone is firm but not hostile. He also begins chanting the Maṅgala mantra: “Om Aṅgārakāya Namaḥ.” Before the meeting, he does ten minutes of Kapālabhāti prāṇāyāma to activate the Solar Plexus.

Outcome: The Saṃskāra of passive collapse is met with disciplined fire. Even if the meeting doesn’t change the manager’s behaviour, Arun has changed his own inner pattern. The groove of suppression begins to weaken. Mars finds its voice—not as rage, but as self-respect.

✦  ✦  ✦', 3),
    (18, 'budha', 'Budha', NULL, 'The Principle of Intellect and Communication', 'Budha governs the discriminative intellect—the capacity to analyze, categorize, communicate, and adapt. In the body, it rules the nervous system, the hands, the skin, and the respiratory passages. In the psyche, it represents analytical intelligence, verbal facility, commercial acumen, and the ability to navigate complexity. Budha’s Daśā period is seventeen years.

Equilibrium: The Healthy Mercurial Principle

Somatic Base:

The nervous system is calibrated and responsive without being reactive. The hands are dexterous and expressive. Breathing is even and easy. There is a lightness to the body—an agility that allows rapid adaptation to changing physical demands. The skin is clear and sensitive to touch.

Emotional Current:

There is a playful, curious quality to the emotional life. Budha enjoys variety, novelty, and the pleasures of learning. Relationships are characterized by good communication—the ability to articulate feelings with precision, to listen with genuine interest, and to find the right word at the right moment. Humour is available and skilful.

Cognitive Map:

Thinking is quick, versatile, and analytically sharp. The mind can hold multiple perspectives simultaneously without confusion. There is a facility with language—spoken, written, or symbolic—that makes complex ideas accessible. The internal narrative is curious: “Let me understand this. What are the pieces? How do they fit together?”

Inner Presence:

The soul experiences the world as an intricate puzzle worthy of patient engagement. There is a delight in the structure of reality—in patterns, connections, and the elegance of well-ordered thought. Budha at its highest serves Vijñāna—discriminative wisdom that distinguishes the real from the apparent.

Excess: Mercurial Overdrive

Somatic Base:

The nervous system is over-stimulated and dysregulated. Hands tremor; the fingers tap incessantly. Breathing becomes shallow and rapid. Sleep is disrupted by a racing mind that cannot stop generating thoughts. Skin conditions flare—eczema, rashes—as the nervous system overflows into the body’s largest organ. There is a frantic, wired quality: always moving, never still.

Emotional Current:

Anxiety replaces curiosity. The mind’s speed, which in equilibrium produces insight, now produces panic. There is a scattered quality to emotional life—dozens of half-felt feelings that are categorized before they are fully experienced. Relationships suffer from over-analysis: “What did they mean by that? Should I read between the lines?” Communication becomes verbose, tangential, or evasive.

Cognitive Map:

Overthinking becomes chronic. Analysis paralysis sets in. Every decision spawns ten sub-decisions, each requiring further analysis. The internal narrative is a caffeinated hamster-wheel: “But what about this? And what if that? And have I considered...” Knowledge is accumulated compulsively without integration. Information becomes a defence against feeling.

Inner Presence:

The intellect has become the soul’s cage. The individual is trapped in the Manomaya Kośa, mistaking mental activity for spiritual progress. Meditation becomes another analytical exercise. The lesson is the discovery that silence is more intelligent than any thought.

Deficiency: Mercurial Dimming

Somatic Base:

The nervous system is sluggish. Coordination is impaired; the hands feel clumsy. Speech is slow or unclear. Respiratory issues—shallow breathing, chronic throat clearing—reflect the dimmed Budha. Learning new physical skills feels difficult. There is a heaviness to the nervous system, as though signals travel through fog.

Emotional Current:

Communication becomes impaired. One struggles to articulate feelings, often saying the wrong thing or saying nothing at all. There is a frustrating gap between what is felt internally and what can be expressed. Relationships suffer from miscommunication and misunderstanding. Humour is absent; conversation feels laboured.

Cognitive Map:

Thinking is slow, rigid, and concrete. Abstraction is difficult. The mind cannot hold multiple perspectives; it fixates on a single interpretation and defends it stubbornly. The internal narrative is flat and repetitive: the same few thoughts cycle without variation or development.

Inner Presence:

The discriminative faculty that allows the soul to distinguish Self from not-Self is impaired. Confusion between essential truths and surface appearances dominates. The spiritual lesson is the patient cultivation of clarity—through study (Svādhyāya), journaling, or guided dialogue with a teacher.

✦  ✦  ✦', 4),
    (18, 'sukra', 'Śukra', NULL, 'The Principle of Beauty, Harmony, and Relationship', 'Śukra governs the realm of desire, beauty, sensory pleasure, and relational harmony. In the body, it rules the kidneys, reproductive organs, skin, and the sense of taste. In the psyche, it represents the capacity for love, aesthetic sensitivity, artistic expression, and the longing for connection. Śukra’s Daśā period is twenty years—the longest of any Graha—reflecting the enduring and pervasive nature of desire in human life.

Equilibrium: The Healthy Venusian Principle

Somatic Base:

The body feels beautiful to inhabit. There is a smoothness to the skin, a grace to movement, a sensitivity to texture, colour, and sound that makes sensory experience rich and pleasurable. Reproductive health is balanced. The kidneys function well; the body’s internal chemistry is harmonious. There is a natural inclination toward cleanliness, pleasant clothing, and environments that are aesthetically ordered.

Emotional Current:

Love flows easily—not as desperate clinging or passionate infatuation, but as a warm, steady appreciation for the beauty in others and in the world. Relationships are characterised by reciprocity, sensual attentiveness, and genuine delight in the partner’s existence. There is a capacity for romantic love that does not consume the lover, and a capacity for friendship that includes loyalty without possessiveness.

Cognitive Map:

Thinking includes the aesthetic dimension. One evaluates not only whether something is true or useful, but whether it is beautiful, harmonious, and life-enhancing. The internal narrative includes: “Does this environment nourish me? Is this arrangement pleasing? Does this relationship create more beauty or more friction?” Art, music, and poetry are not luxuries but necessities for cognitive balance.

Inner Presence:

The soul perceives the world as an expression of divine beauty (Sundaram). Every sensory experience becomes a portal to the sacred—the sunset, the taste of food prepared with love, the touch of a beloved hand. Śukra at its highest transforms sensory pleasure from a trap into a path of devotion (Bhakti).

Excess: Venusian Indulgence

Somatic Base:

The body becomes the site of compulsive pleasure-seeking. Over-eating, over-sleeping, and over-indulgence in sensory comforts lead to weight gain, metabolic sluggishness, and Kapha aggravation. Skin becomes thick or congested. Reproductive issues may arise from excess—hormonal imbalances, cysts, or infections related to over-activity. The body craves sweetness in all forms: sugar, comfort, softness.

Emotional Current:

Love becomes possessive. Desire becomes addiction. The partner is no longer a person but a source of pleasure whose absence triggers panic. Jealousy, romantic obsession, and codependency dominate the emotional landscape. When the desired object or person is unavailable, the emotional system crashes into despair. Beauty becomes another form of grasping—an endless pursuit of the next beautiful thing, person, or experience.

Cognitive Map:

Thinking becomes hedonistic and short-sighted. The calculus of every decision is: “Will this feel good?” Consequences are minimized; gratification is maximized. The internal narrative is a catalogue of wants: “I want that. I need this. When will I get the next dose of pleasure?” Difficult truths are avoided because they are ugly.

Inner Presence:

The soul is buried under layers of sensory stimulation. The divine beauty that Venus can reveal is obscured by the compulsive consumption of its worldly reflections. The spiritual lesson is Vairāgya—discernment between pleasure that elevates and pleasure that binds.

Deficiency: Venusian Starvation

Somatic Base:

The body feels utilitarian and joyless. There is no sensory pleasure—food has no taste, the world has no colour. Skin is dry and rough. Reproductive vitality is low. The environment is neglected: messy, colourless, stripped of any beauty. The body is treated as a machine to be fuelled rather than a temple to be honoured.

Emotional Current:

The capacity for love is impaired. Relationships feel empty or purely functional. Intimacy is avoided because it feels dangerous or embarrassing. There is a deep loneliness that cannot be articulated because the language of desire has been muted. The emotional tone is grey—a flatland without the peaks of joy or the valleys of longing.

Cognitive Map:

Thinking is purely utilitarian. Beauty, art, and sensory richness are dismissed as frivolous. The internal narrative: “What’s the point of flowers? Life is about productivity.” Relationships are evaluated solely by what they produce rather than how they feel. There is a poverty of imagination—a cognitive landscape stripped of colour.

Inner Presence:

The soul has forgotten that the world is beautiful. The divine’s expression through form—which is Śukra’s highest teaching—has been denied. The spiritual lesson is the re-enchantment of daily life: the discovery that cooking a meal with care, arranging flowers, or listening to music with full attention can be a practice of presence as potent as meditation.

Vignette: The Online Shopping Spiral

Scenario A: The Binding Path (Low Epistemic Integrity)

Context: Priya, 31, is going through a difficult period in her marriage. Śukra is currently transiting her 8th house (transformation and crisis), activating themes of emotional deprivation.

Internal Landscape: After another evening of strained silence with her husband, Priya opens a shopping app. A warm, tingling sensation spreads through her chest as she browses luxury skincare. “I deserve something beautiful. At least this won’t disappoint me.” She mislabels her emotional hunger for intimacy as a desire for objects. The Venusian craving is real, but its target is misidentified.

Conduct: Priya orders four hundred dollars of products she does not need. The packages arrive and produce a brief dopamine surge that fades within hours. The credit card bill arrives; guilt compounds the original sadness.

Outcome: The Saṃskāra of substituting objects for intimacy deepens. The Vāsanā for consumption-as-comfort hardens. The actual relational wound remains unaddressed, gathering pressure.

Scenario B: The Liberating Path (High Epistemic Integrity)

Internal Landscape: Priya feels the pull of the shopping app. She pauses. “This isn’t about skincare. This is the loneliness. The Venus-transit is amplifying the ache for connection. What I actually want is to feel beautiful to someone—to feel desired, seen, cherished.”

Conduct: Priya puts the phone down. She draws a bath, adds rose oil (Śukra’s flower), lights a candle, and sits with the ache rather than numbing it. Later, she writes in her journal: a letter to her husband she may or may not send, articulating what she misses in their marriage. The next day, she suggests they attend a couples’ retreat. This is Bhakti-as-relational-practice—turning toward the beloved rather than away.

Outcome: The Saṃskāra of consumption-as-anaesthesia is met with honest naming. The Eṣaṇā for comfort does not vanish, but its aim is redirected from objects to genuine relationship. The Venus-transit becomes a teacher rather than a tormentor.

✦  ✦  ✦', 5),
    (18, 'guru_brhaspati', 'Guru/Bṛhaspati', NULL, 'The Principle of Wisdom and Expansion', 'Guru governs Dharma—the moral order, higher purpose, and the capacity for wisdom. In the body, it rules the liver, pancreas, and fat metabolism. In the psyche, it represents optimism, generosity, philosophical inclination, the teacher-student relationship, and the capacity to see the larger pattern in which individual events are embedded.

Equilibrium: The Healthy Jupiterian Principle

Somatic Base:

The body is well-nourished and proportionate. The liver functions optimally; metabolism is balanced. There is a physical generosity—a largeness to the frame that feels comfortable rather than excessive. Energy is sustained and even. The appetite for food is healthy and inclusive—one enjoys eating without being driven by it.

Emotional Current:

There is a buoyant, hopeful quality to emotional life. Setbacks are absorbed without despair because they are seen within a larger context of meaning. Generosity flows naturally—with time, attention, and resources. There is an emotional grandeur: the capacity to feel deeply moved by beauty, justice, or the suffering of others. Relationships with teachers and mentors are healthy and reciprocal.

Cognitive Map:

Thinking is panoramic and meaning-oriented. The mind naturally seeks the “big picture”—synthesizing disparate information into coherent frameworks. There is a philosophical disposition: not merely “What happened?” but “What does it mean? What is the deeper lesson?” Ethics are integrated into decision-making, not as imposed rules but as felt imperatives.

Inner Presence:

The soul experiences itself as a student of the divine. There is an authentic faith—not blind belief, but a trust in the meaningful structure of existence. The guru principle operates within: there is an inner teacher whose quiet counsel can be heard in moments of stillness.

Excess: Jupiterian Inflation

Somatic Base:

The body expands beyond its appropriate limits. Weight gain, liver congestion, high cholesterol, and metabolic syndrome reflect the unchecked Jupiterian impulse to take in more than one can process. The appetite becomes indiscriminate. There is a physical smugness—a self-satisfied corpulence.

Emotional Current:

Optimism becomes delusion. The individual cannot perceive genuine danger because every cloud has a silver lining, every failure is a “blessing in disguise.” Generosity becomes enabling—giving beyond one’s capacity, creating resentment underneath the veneer of beneficence. There is a moral superiority that alienates others: “I know what’s best for you.”

Cognitive Map:

Thinking becomes grandiose and ungrounded. Plans are vast but lack practical foundation. The mind confuses expansion with progress. Philosophical frameworks become cages rather than maps—rigid belief systems that explain everything while understanding nothing. The internal narrative: “It’s all part of the plan. Trust the process.”—even when the plan is failing and the process needs revision.

Inner Presence:

The soul confuses spiritual knowledge with spiritual attainment. The individual becomes a guru to others before completing their own education. There is a spiritual materialism—accumulating teachings, initiations, and lineages as status symbols. The lesson is humility: the recognition that true wisdom begins with admitting how much one does not know.

Deficiency: Jupiterian Contraction

Somatic Base:

The liver is sluggish; growth is stunted or inadequate. The body feels malnourished at a cellular level, even if caloric intake is sufficient. There is a thinness that is not healthy but depleted—a body that has not been properly nourished by joy, generosity, or meaning.

Emotional Current:

Cynicism replaces hope. The world appears meaningless, arbitrary, and devoid of grace. Generosity is absent—not from cruelty but from a conviction that there is not enough (time, money, love) to share. Relationships with teachers are broken or nonexistent; the individual trusts no authority. The emotional tone is a flat, existential despair that does not announce itself dramatically but erodes the quality of every day.

Cognitive Map:

Thinking is narrow and purposeless. The “big picture” is invisible. Decisions are made on the basis of short-term survival rather than long-term meaning. Ethics feel irrelevant—“What’s the point of being good in a world that doesn’t care?” Philosophy is dismissed as “useless abstraction.” Education feels pointless.

Inner Presence:

The soul has lost contact with its own deepest purpose. The inner guru is silent. There is a spiritual void—not atheism (which can be philosophically robust) but an aching absence of meaning that cannot be filled by material success alone. The lesson is the willingness to seek again: to open a book, attend a teaching, ask a genuine question.

✦  ✦  ✦', 6),
    (18, 'sani', 'Śani', NULL, 'The Principle of Discipline, Time, and Karmic Reckoning', '"Karmaphala-dātā Śaniścaraḥ"

(Saturn is the bestower of the fruits of Karma.)

— Jyotiṣ tradition

Śani is the most feared and the most misunderstood of the Grahas. It governs the principle of time (Kāla), limitation, structure, discipline, and the slow, inevitable reckoning of karmic debt. In the body, it rules the bones, teeth, joints, and the ageing process itself. In the psyche, it represents perseverance, responsibility, melancholy, humility, and the capacity to endure. Śani’s Daśā period is nineteen years; its seven-and-a-half-year transit through the houses surrounding the natal Moon (Sāḍe Sāti) is regarded as the most significant karmic passage in an individual’s life.

Equilibrium: The Healthy Saturnine Principle

Somatic Base:

The body is lean, strong, and enduring. Bones are dense; joints are stable. There is a structural integrity to the frame that withstands time and strain. Energy is not abundant but consistent—a slow-burning fire that sustains effort over decades. The body ages gracefully, each line and mark earned through honest living.

Emotional Current:

There is a quiet seriousness to the emotional life that is not depression but gravitas. The individual can tolerate discomfort, delay gratification, and sit with ambiguity without panic. There is a deep loyalty—commitments are honoured even when inconvenient. Emotional maturity manifests as the capacity to hold sadness without being destroyed by it, to acknowledge limitation without resentment.

Cognitive Map:

Thinking is patient, methodical, and realistic. Plans are grounded in what is achievable rather than what is thrilling. The internal narrative values process over outcome: “How did I earn this? What did I build, brick by brick?” There is a respect for tradition, for structures that have survived the test of time, and for the slow accumulation of mastery through repetition.

Inner Presence:

The soul understands itself as a worker in the field of time. There is no impatience with the pace of spiritual progress; there is instead a trust in the process of gradual maturation. The individual serves—not for applause, but because service is the debt one pays for the privilege of existence. Saturn at its highest is Karma Yoga embodied: disciplined action offered without attachment to result.

Excess: Saturnine Petrification (“Too Much Saturn”)

Somatic Base:

The body stiffens and contracts. Chronic joint pain, arthritis, bone spurs, and dental problems are common. There is a calcification—physical structures that should be flexible become rigid. Skin becomes thick and dry. The body ages prematurely, not with grace but with punishment. Chronic constipation reflects the psychological holding pattern.

Emotional Current:

Discipline becomes rigidity. Stoicism becomes emotional deadness. The individual cannot celebrate, cannot receive pleasure, cannot soften. Every joy is met with suspicion: “It won’t last. Don’t get attached.” Fear becomes the dominant emotional register—not acute fear, but a pervasive, grinding dread that life will punish any moment of relaxation. Relationships are burdened by excessive duty and absent of warmth.

Cognitive Map:

Thinking becomes pessimistic and hyper-conservative. Every plan is stress-tested to the point of paralysis. The internal narrative: “Nothing good lasts. It’s better not to try than to fail. Lower your expectations.” Innovation is distrusted. Change is resisted. The mind becomes a fortress that keeps danger out but also keeps life out.

Inner Presence:

The soul has mistaken suffering for virtue. There is a martyrdom complex—a belief that one earns spiritual credit through deprivation rather than through conscious engagement. The lesson is the discovery that Saturn’s discipline is meant to build a structure within which joy can safely exist—not to eliminate joy altogether.

Deficiency: Saturnine Collapse (“Too Little Saturn”)

Somatic Base:

The skeletal structure is weak. Bones are fragile; teeth deteriorate early. There is a lack of physical endurance—the body tires quickly and recovers slowly. Posture is poor, not from emotional collapse (as with weak Sun) but from structural inadequacy. The body lacks the “frame” upon which health depends.

Emotional Current:

Discipline is absent. Commitments are made and broken casually. Responsibility is avoided. The emotional life is governed by the pleasure principle: whatever feels good now is pursued, regardless of long-term consequences. There is an emotional adolescence—a refusal to accept the constraints of adult life. Relationships lack depth because they lack endurance.

Cognitive Map:

Thinking is short-sighted and undisciplined. Plans are never completed because the next shiny idea replaces the current one. The internal narrative avoids any mention of consequences: “Why worry? It’ll work out.” Hard truths are evaded. Deadlines are missed. The mind has no scaffolding upon which to build sustained intellectual achievement.

Inner Presence:

The soul avoids its karmic curriculum. The lessons that Saturn presents—patience, humility, accountability—are refused or postponed. The individual may be spiritually sincere but spiritually unstructured: they read many books but complete no practice; they begin many paths but walk none to its end. The lesson is commitment: choosing one practice, one discipline, one path, and staying on it through boredom, difficulty, and the temptation to flee.

Vignette: The Sāḍe Sāti Season

Scenario A: The Binding Path (Low Epistemic Integrity)

Context: Deepak, 50, has entered Sāḍe Sāti—Saturn’s seven-and-a-half-year transit through his natal Moon sign. In the past eighteen months: his mother has died, his eldest child has left for university, and his company has been restructured, leaving him in a diminished role.

Internal Landscape: Deepak wakes each morning to a heaviness that sits on his chest like wet stone. His joints ache. The world appears in greyscale. “This is punishment. I must have done something terrible in a past life. The stars are against me.” He externalizes Saturn’s influence as persecution rather than pedagogy. He consults an astrologer who prescribes a blue sapphire ring—but Deepak wears it as a talisman against fate rather than a tool for attunement.

Conduct: Deepak withdraws. He stops calling friends. He works mechanically, without investment. He sits in front of the television for hours, numbed. His wife’s attempts at warmth are rebuffed: “You don’t understand.” The Sāḍe Sāti period becomes a long, grey tunnel that he endures rather than engages.

Outcome: The Saṃskāra of passive victimhood hardens. The period ends, as all transits do, but Deepak emerges from it diminished rather than deepened. The karmic curriculum was presented; he did not enroll. The same lessons will return in another form.

Scenario B: The Liberating Path (High Epistemic Integrity)

Internal Landscape: Deepak feels the same heaviness. But he has been studying his chart with a wise counsellor who framed Sāḍe Sāti not as punishment but as purification. “This is Saturn’s classroom. The curriculum is loss, limitation, and the discovery of what remains when everything non-essential is stripped away.” He does not deny the grief. He sits with it, names it, and asks: “What is Saturn asking me to become?”

Conduct: Deepak begins a practice of disciplined simplicity. He rises at 5 a.m. and walks for one hour in silence—Saturn’s medicine of slow, sustained effort. He volunteers at a hospice (Saturn governs the elderly and the dying). He fasts on Saturdays, not as superstitious observance but as a conscious meeting with limitation. He begins to journal—recording not what he has lost, but what each loss has revealed about what he truly values. He lights a sesame oil lamp on Saturday evenings and chants: “Om Śanaiścaraya Namaḥ.”

Outcome: The Saṃskāra of victimhood is met with disciplined engagement. The grief does not disappear, but it transmutes into depth. Deepak emerges from Sāḍe Sāti leaner, quieter, and more honest. His relationships, while fewer, are now founded on genuine presence rather than social performance. Saturn’s lesson has been received: the discovery that one can lose everything that can be lost and still stand.

✦  ✦  ✦', 7),
    (18, 'rahu', 'Rāhu', NULL, 'The Principle of Worldly Obsession and Karmic Hunger', 'Rāhu represents the point of maximum worldly desire, amplification, and illusion. It has no body—only a head—and therefore its appetite is literally insatiable: it consumes but can never be filled. In the psyche, Rāhu manifests as compulsive ambition, fascination with the foreign or unconventional, technological obsession, and the pursuit of experiences that one has never had before. Rāhu’s Daśā period is eighteen years.

Equilibrium: Rāhu as Evolutionary Driver

Somatic Base:

When Rāhu’s energy is well-channelled, it manifests as a heightened sensitivity to environmental stimuli—a capacity to pick up on subtle cues that others miss. The nervous system is alert without being frayed. There is an adaptability in the body that allows one to thrive in unfamiliar settings—new countries, new climates, new physical demands.

Emotional Current:

There is an excitement about the unknown that is not manic but genuinely curious. The individual can engage with foreign cultures, unconventional ideas, and taboo subjects without being consumed by them. There is a healthy ambition—a desire to grow beyond one’s current station—that is tempered by awareness of its source in karmic need rather than genuine necessity.

Cognitive Map:

Thinking is innovative and boundary-breaking. The individual questions conventions and sees possibilities that others cannot. There is a natural affinity for technology, research, and paradigm-shifting ideas. The cognitive style is synthetic—combining elements from different domains in novel ways.

Inner Presence:

The soul understands Rāhu as a teacher of expansion—a force that pushes consciousness into unfamiliar territory precisely because comfort zones have become spiritual stagnation points. The hunger is honoured, but not obeyed blindly.

Excess: Rāhu as Obsessive Compulsion

Somatic Base:

The nervous system is over-stimulated and dysregulated. Unusual or undiagnosed symptoms arise—strange pains, hypersensitivities, phantom sensations. The body feels as though it is being driven by an engine with no off-switch. Addictive patterns emerge: substances, screens, or compulsive behaviours that provide temporary relief from the relentless inner hunger. Sleep is disturbed by vivid, sometimes disturbing dreams.

Emotional Current:

Desire becomes obsession. The individual fixates on a particular person, goal, or experience with an intensity that is disproportionate to its actual value. There is a quality of “spell”—a feeling of being under the influence of a force one cannot control. Anxiety is chronic and free-floating, attaching itself to whatever object is nearest. There is a sense that something is desperately wrong, but it cannot be named.

Cognitive Map:

Thinking becomes conspiratorial and paranoid. The mind weaves elaborate narratives to justify its obsessions. Illusion is mistaken for insight. The individual may become fixated on conspiracy theories, occult practices without grounding, or grandiose visions of world-changing significance. The internal narrative: “Only I can see the truth. Everyone else is asleep.”

Inner Presence:

The soul is lost in Māyā—the cosmic illusion. Rāhu’s shadow has eclipsed the inner light, and the individual cannot distinguish genuine spiritual prompting from karmic compulsion. The lesson is devastating and simple: what you most desperately want is not what you most deeply need.

Deficiency: Rāhu Suppressed

Somatic Base:

The body feels paralyzed in its comfort zone. There is an inability to adapt to new environments, new foods, new climates. The nervous system is under-responsive to novelty—dull, sluggish, and resistant to change. Chronic conditions of stagnation may develop.

Emotional Current:

Fear of the unknown dominates. Anything foreign, unconventional, or challenging is avoided. The individual clings to the familiar with a rigidity that prevents growth. Relationships are limited to a very small circle, and any disruption to the routine triggers disproportionate distress.

Cognitive Map:

Thinking is provincial and closed. New ideas are rejected without examination. The cognitive style is purely reproductive—repeating what has already been learned rather than generating new understanding. Innovation is impossible because the mind has walled itself off from the discomfort that innovation requires.

Inner Presence:

The soul refuses its own evolutionary curriculum. The growth that Rāhu demands is denied. Life becomes a repetition of patterns that were mastered long ago, and the resulting existential boredom slowly poisons every domain.

✦  ✦  ✦', 8),
    (18, 'ketu', 'Ketu', NULL, 'The Principle of Detachment and Spiritual Liberation', 'Ketu is Rāhu’s counterpart and complement. Where Rāhu reaches forward into the unknown, Ketu points backward to what has already been completed. It represents past-life mastery, spiritual insight, the capacity for detachment, and the dissolution of worldly attachment. In the body, Ketu is associated with the lower limbs and with mysterious, untraceable ailments. In the psyche, it represents mysticism, psychic sensitivity, liberation, and the willingness to let go. Ketu’s Daśā period is seven years.

Equilibrium: Ketu as Spiritual Wisdom

Somatic Base:

When Ketu’s energy is integrated, there is a lightness to the body that reflects the absence of excessive attachment. The individual does not cling to physical comfort; they can fast, sit in stillness, or endure austerity without suffering. There is an intuitive body-awareness that does not require external tools—the body “knows” what it needs without elaborate analysis.

Emotional Current:

There is a serene detachment that is not coldness but clarity. The individual can witness the arising and passing of emotions without being destabilized by them. There is no fear of loss because there is a deep understanding that nothing real can be lost. Relationships are held lightly—with genuine love but without grasping.

Cognitive Map:

Thinking is penetrative and non-verbal. The individual understands through direct perception rather than elaborate reasoning. There is an affinity for the mystical, the paradoxical, and the ineffable. The internal narrative is sparse: much is understood that cannot be articulated, and there is peace with that limitation.

Inner Presence:

The soul is in contact with its own deepest nature. The layers of identification—with body, mind, emotion, role—are transparent. There is a lived sense of what the Śāstras describe as “the witness”—the consciousness that observes experience without being identical to it. Ketu at its highest is Mokṣa itself: liberation from the cycle of becoming.

Excess: Ketu as Dissociation

Somatic Base:

The body feels unreal—as though one is observing it from outside. Dissociation manifests physically as numbness, clumsiness, or a strange disconnect between intention and movement. There may be mysterious symptoms—pains without physical cause, sensitivities without explanation—that reflect Ketu’s fundamental nature as a headless body groping in the dark.

Emotional Current:

Detachment becomes indifference. The individual cannot engage emotionally with life—not because they have transcended emotion, but because they have disengaged from it prematurely. Relationships wither from neglect. There is a ghostly quality—present in body but absent in spirit. The person seems to be always somewhere else.

Cognitive Map:

Thinking becomes nebulous and unfocused. Mysticism replaces clear reasoning. The individual may claim profound spiritual insight while being unable to function in daily life—unable to pay bills, maintain a schedule, or complete ordinary tasks. The internal narrative: “The material world doesn’t matter. I am beyond all this.” But “beyond” is really “in retreat from.”

Inner Presence:

The soul uses spirituality as an escape from incarnation rather than as a path through it. Ketu’s gift of non-attachment has been perverted into avoidance. The lesson is that Mokṣa is not achieved by refusing to engage with life, but by engaging so fully and so consciously that attachment naturally dissolves.

Deficiency: Ketu Suppressed

Somatic Base:

The body is entirely identified with worldly pursuit—health is maintained for productivity, appearance is curated for social advantage, and physical discipline serves ambition rather than awareness. There is no capacity for stillness; meditation is impossible not because the mind is restless but because the body demands constant stimulation.

Emotional Current:

There is no access to the contemplative dimension of emotional life. Every feeling is channelled into action. Grief is “processed” through work. Loneliness is “solved” through socializing. The deeper currents—the existential longing for meaning, the intuition of something beyond the visible—are walled off entirely.

Cognitive Map:

Thinking is entirely materialistic and empirical. The invisible dimension of experience is denied or mocked. Spirituality is dismissed as superstition. The internal narrative: “Only what I can see and measure is real.” This is not philosophical empiricism but an existential flinch—a refusal to confront the mystery at the heart of being.

Inner Presence:

The soul is fully identified with its worldly roles—professional, familial, social—and has forgotten that it is, at its core, something that cannot be defined by any role. The lesson is the first encounter with genuine emptiness: the moment when all external identifiers fail and the question “Who am I really?” can no longer be evaded.

Vignette: The Career Pivot at Forty-Five

Scenario A: The Binding Path (Low Epistemic Integrity)

Context: Sunita, 45, is a successful corporate lawyer who has entered her Ketu Daśā. For the first time in her career, her work feels hollow. She wins a major case and feels nothing.

Internal Landscape: Sunita is bewildered. “This is what I worked twenty years for. Why do I feel empty?” Rather than recognizing the Ketu Daśā as an invitation to explore what lies beyond professional identity, she panics. She mislabels the detachment as depression and the hollowness as burnout. She decides what she needs is more —a bigger case, a higher-profile client, a book deal.

Conduct: Sunita doubles down on work. She takes on pro bono cases not out of service but out of a desperate need to feel the old surge of purpose. She starts a podcast about legal strategy, hoping public visibility will fill the void. The emptiness deepens.

Outcome: The Saṃskāra of identity-through-achievement hardens even as Ketu systematically undermines its foundations. The Vāsanā for professional validation becomes more frantic as its returns diminish. Sunita is running faster on a treadmill that is slowing down.

Scenario B: The Liberating Path (High Epistemic Integrity)

Internal Landscape: Sunita notices the emptiness and, instead of fleeing, sits down inside it. “This isn’t depression. This is Ketu. This is the soul saying: you’ve completed this lesson. The things that gave you identity—the titles, the wins, the recognition—are being gently removed not as punishment, but as preparation. Something else is trying to emerge.”

Conduct: Sunita does not quit her job impulsively. But she begins to create space. She takes a three-month sabbatical. She visits an ashram—not to “find herself” in a consumerist sense, but to sit in the silence that Ketu demands. She begins a daily practice of Viśpassanā meditation—the practice most aligned with Ketu’s energy, which involves observing the arising and passing of all phenomena without attachment. She donates anonymously to causes she cares about, releasing the need for recognition (a Ketu practice).

Outcome: The Saṃskāra of identity-through-achievement is met with conscious dissolution. The Eṣaṇā for recognition loosens. Sunita does not become a “spiritual person” in the performative sense; she becomes someone for whom the question “Who am I?” is no longer terrifying but generative. When she returns to law, she practises differently—with less ego and more service. The title remains; the attachment to it dissolves.

✦  ✦  ✦', 9);

COMMIT;

-- Sanity checks (uncomment to run):
-- SELECT dimension_id, COUNT(*) FROM svarupa_concepts GROUP BY dimension_id ORDER BY dimension_id;
-- SELECT COUNT(*) AS concept_descriptions FROM svarupa_concept_descriptions;
