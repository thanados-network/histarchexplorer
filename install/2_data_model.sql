--
-- PostgreSQL database dump
--

\restrict K5X8QF25Wg1QgD8OLPhHrApTdcpAtvNgDEQCqg3idMwy1oYp9B8oyAPvtAM003T

-- Dumped from database version 17.7 (Debian 17.7-0+deb13u1)
-- Dumped by pg_dump version 17.7 (Debian 17.7-0+deb13u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: classes; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

INSERT INTO tng.classes OVERRIDING SYSTEM VALUE VALUES
	(1, 'project'),
	(2, 'person'),
	(4, 'institution'),
	(5, 'main-project'),
	(6, 'language_code'),
	(3, 'attribute');


--
-- Data for Name: entities; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

INSERT INTO tng.entities OVERRIDING SYSTEM VALUE VALUES
	(5, '{"de": "Projektleitung", "en": "Principal Investigator"}', NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(9, '{"de": "Design & Programmierung", "en": "Design & Programming"}', NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(12, '{"de": "Datenaufnahme", "en": "Data Acquisition"}', NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(14, '{"de": "Sponsor", "en": "Sponsor"}', NULL, NULL, 3, 'https://example.example', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(15, '{"de": "Partner", "en": "Partner"}', NULL, NULL, 3, 'https://example.example', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(22, '{"de": "Nina Richards", "en": "Nina Richards"}', '{"de": "<p>... hat einen Master in Arch&auml;ologie des Mittelalters und der Neuzeit von der Universit&auml;t Bamberg (DE). Sie hat au&szlig;erdem einen Bachelorabschluss in Biologie mit Schwerpunkt auf Anthropologie der Universit&auml;t Wien. Sie hat bereits an der Universit&auml;t Wien und am &Ouml;sterreichischen Arch&auml;ologischen Institut als (Praedoc) Wissenschaftlerin in den Bereichen Arch&auml;ologie, Biologische Anthropologie und Digital Humanities. Sie ist Co-Leiterin des&nbsp;<a href=\"https://thanados.net/\" target=\"_blank\" rel=\"noopener noreferrer\">THANADOS</a>-Projekts.</p>", "en": "<p>... has a Master''s degree in Archaeology of the Middle Ages and Modern Times from the University of Bamberg (DE). She also completed a bachelor''s degree in biology with a focus on anthropology at the University of Vienna. She worked at the University of Vienna and the Austrian Archaeological Institute as a (predoctoral) researcher in the field of archaeology, physical anthropology, and digital humanities. She is Co-PI of the&nbsp;<a href=\"https://thanados.net/\" target=\"_blank\" rel=\"noopener noreferrer\">THANADOS</a> project.</p>"}', '{}', 2, NULL, '0000-0002-4911-8451', NULL, NULL, '{}', '{}', NULL, ''),
	(21, '{"de": "Austrian Centre for Digital Humanities", "en": "Austrian Centre for Digital Humanities & Cultural Heritage"}', '{}', '{"de": "Bäckerstraße 13\r\n1010 Wien"}', 4, 'ACDH-CH-Office@oeaw.ac.at', NULL, 'https://www.oeaw.ac.at/fileadmin/oeaw/institutstemplate/acdh/img/acdh-ch-logo96.png', 'https://www.oeaw.ac.at/acdh/acdh-ch-home', '{}', '{}', NULL, 'ACDH'),
	(34, '{"de": "Hostinstitut"}', '{}', '{}', 3, NULL, NULL, NULL, NULL, '{}', '{}', 0, ''),
	(20, '{"de": "Universität Wien", "en": "University of Vienna"}', '{"de": "Die Wiener Uni", "en": "Viennese university"}', '{"de": "Universitätsring 1\r\n1010 Wien", "en": "Universitätsring 1\r\n1010 Vienna"}', 4, 'uni@univie.ac.at', NULL, 'https://www.univie.ac.at/fileadmin/user_upload/univie/Logos/Logos_Universitaet_Wien/Uni_Logo.jpg', 'https://www.univie.ac.at/', '{}', '{}', NULL, 'Uni Wien'),
	(3, '{"de": "Lisa Aldrian", "en": "Lisa Aldrian"}', '{}', '{}', 2, NULL, '0000-0001-5176-8421', NULL, NULL, '{}', '{}', NULL, ''),
	(19, '{"de": "Naturhistorisches Museum Wien", "en": "Museum of Natural History Vienna"}', '{"de": "<p>Naturhistorisches Museum</p>", "en": "<p>Naturhistorisches Museum</p>"}', '{"de": "Burgring 7", "en": "Burgring 7"}', 4, NULL, NULL, 'https://nhm.at/jart/prj3/nhm-resp/resources/images/logo.svg', 'https://nhm.at/', '{}', '{}', NULL, 'NHM'),
	(6, '{"de": "Hauptkoordinator*in", "en": "Main Coordinator"}', '{}', '{}', 3, NULL, NULL, NULL, NULL, '{}', '{}', NULL, ''),
	(4, '{"de": "David Ruß", "en": "David Ruß"}', '{}', '{}', 2, NULL, '0000-0002-2429-3747', NULL, NULL, '{}', '{}', NULL, ''),
	(10, '{"de": "Archäolog*in", "en": "Archaeologist"}', '{}', '{}', 3, NULL, NULL, NULL, NULL, '{}', '{}', NULL, ''),
	(7, '{"de": "Forscher*in", "en": "Researcher"}', '{}', '{}', 3, NULL, NULL, NULL, NULL, '{}', '{}', NULL, ''),
	(13, '{"de": "Historiker*in", "en": "Historian"}', '{}', '{}', 3, NULL, NULL, NULL, NULL, '{}', '{}', NULL, ''),
	(11, '{"de": "Anthropolog*in", "en": "Anthropologist"}', '{}', '{}', 3, NULL, NULL, NULL, NULL, '{}', '{}', NULL, ''),
	(8, '{"de": "Softwareentwickler*in", "en": "Software Developer"}', '{}', '{}', 3, NULL, NULL, NULL, NULL, '{}', '{}', NULL, ''),
	(17, '{"de": "Modelling Religiopolitics. The Imperium Christianum via its Commoners", "en": "Modelling Religiopolitics. The Imperium Christianum via its Commoners"}', '{"de": "<p><strong>RELIC&nbsp;</strong>ist ein Forschungsprojekt, das l&auml;ndliche Gemeinschaften an der &ouml;stlichen Peripherie des Heiligen R&ouml;mischen Reiches im 10.&ndash;12. Jahrhundert untersucht und ihre Rolle bei Christianisierung, Staatsbildung und kirchlicher Organisation analysiert.</p>\n<p>Ab dem 10. Jahrhundert entstanden an der Peripherie des Heiligen R&ouml;mischen Reiches neue Herrschaftsgebilde. Die Institutionalisierung des Christentums war ein zentrales Machtinstrument des Kaisers, da sie seinen Einfluss ausweitete und seine Herrschaft in diesen neuen Reichen stabilisierte. Bisherige Darstellungen beruhen &uuml;berwiegend auf wenigen schriftlichen Quellen, die vor allem die oberen gesellschaftlichen Schichten betreffen. Deshalb l&auml;sst sich die weltliche und kirchliche Organisation der Landbev&ouml;lkerung aus diesen Quellen nur unzureichend rekonstruieren, obwohl sie f&uuml;r die Stabilit&auml;t von Staat und Kirche entscheidend war.</p>\n<p><strong>RELIC</strong> f&uuml;hrt eine vergleichende Analyse und Kontextualisierung arch&auml;ologischer und historischer Quellen zur l&auml;ndlichen Bev&ouml;lkerung an den &ouml;stlichen R&auml;ndern des Reiches in ottonischer und salischer Zeit durch. Untersucht werden die Einfl&uuml;sse weltlicher und geistlicher Herrschaft, der nat&uuml;rlichen Umwelt sowie der wirtschaftlichen Infrastruktur auf diese Gemeinschaften. Durch die Konzentration auf diese oft vernachl&auml;ssigte Bev&ouml;lkerungsgruppe wird sichtbar, wie politische und kirchliche Ver&auml;nderungen auf h&ouml;chster Ebene sich in lokalen Strukturen und Kirchennetzen widerspiegelten, welche Strategien in unterschiedlichen politischen Kontexten funktionierten und welche Rolle lokale Initiativen spielten.</p>\n<p>Die religiopolitischen Strukturen des Reiches sind gut erforscht, die Beteiligung der Landbev&ouml;lkerung an diesen Prozessen jedoch kaum. RELIC wendet daher einen neuen methodischen Ansatz an, der N&auml;he-, Netzwerk- und Einzugsgebietsanalysen auf Basis archivalischer arch&auml;ologischer Daten und historischer Quellen kombiniert. F&uuml;r sich genommen sind diese Daten begrenzt; zusammen ergeben sie jedoch einen umfangreichen und bisher unerschlossenen Bestand zur mittelalterlichen Landbev&ouml;lkerung.</p>", "en": "<p><strong>Modelling Religiopolitics. The Imperium Christianum via its Commoners</strong></p>\n<p><strong>RELIC&nbsp;</strong>is a research project that investigates rural communities on the eastern periphery of the Holy Roman Empire during the 10th&ndash;12th centuries and their role in processes of Christianisation, state formation, and ecclesiastical organisation.</p>\n<p>From the 10th century onwards, new polities emerged on the periphery of the Holy Roman Empire (HRE), the new centre of Latin Christendom. Establishing Christianity as an institutional system was integral to imperial power, extending influence and stabilising rule in these new kingdoms. Previous accounts rely mainly on limited written sources focused on political and ecclesiastical elites. As a result, the administrative and ecclesiastical organisation of the rural population cannot be reconstructed satisfactorily from traditional narratives, even though this population was essential for the stability of both Church and State.</p>\n<p><strong>RELIC</strong> conducts a comparative analysis and contextualisation of archaeological and historical evidence related to rural populations on the eastern fringes of the HRE during the Ottonian and Salian periods. It explores how secular and ecclesiastical lordship, environmental conditions, and economic infrastructure shaped local communities. By focusing on this often-overlooked group, the project examines how high-level political and ecclesiastical changes are reflected in local social structures and church networks, how strategies differed across regions, and to what extent local initiatives influenced religious and political transformations.</p>\n<p>&nbsp;</p>\n<p>While the religiopolitical structures of the HRE are well studied, the active involvement of rural populations in these developments has rarely been analysed. RELIC introduces a new approach by combining proximity, network, and catchment analyses using archival archaeological datasets and historical sources. Individually, these data are fragmentary; combined, they form a substantial and previously unexplored corpus on medieval rural society.</p>"}', '{}', 1, NULL, NULL, 'https://thanados.openatlas.eu/api/display/278709.png', NULL, '{}', '{}', 221174, 'RELIC'),
	(2, '{"de": "Stefan Eichert", "en": "Stefan Eichert"}', '{"de": "<p>Stefan Eichert ist wissenschaftlicher Mitarbeiter und stellvertretender Abteilungsdirektor der Abteilung Pr&auml;historie am Naturhistorischen Museum Wien (NHM). Er promovierte an der Universit&auml;t Wien und ist auf fr&uuml;hmittelalterliche, digitale und experimenteller Arch&auml;ologie spezialisiert.<br>Er ist Projektleiter von THANADOS und war ma&szlig;geblich an der Entwicklung und Umsetzung digitaler Forschungsinfrastrukturen beteiligt. Seine Forschung konzentriert sich auf interoperable Datenmodelle und digitale Infrastrukturen f&uuml;r die fr&uuml;hmittelalterliche Arch&auml;ologie, insbesondere im Rahmen von OpenAtlas.<br><br><br></p>", "en": "<p><span>Stefan Eichert</span> is a research associate and deputy head of the Department of Prehistory at the <span>Naturhistorisches Museum Wien</span> (NHM). He earned his doctorate at the <span>University of Vienna</span> and specialises in Early Medieval archaeology, burial archaeology, and experimental archaeology.</p>\n<p>He is Principal Investigator of <span>THANADOS</span> and has been centrally involved in the development of large-scale digital research infrastructures. His research centres on interoperable data models and digital infrastructures for Early Medieval archaeology, notably through <span>OpenAtlas</span>.</p>"}', '{}', 2, NULL, '0000-0002-5827-0797', NULL, NULL, '{}', '{}', NULL, ''),
	(37, '{"de": "Martin Obenaus"}', '{}', '{}', 2, NULL, '0009-0003-1794-5983', NULL, NULL, '{}', '{}', 0, ''),
	(36, '{"de": "Österreichischer Wissenschaftsfonds FWF", "en": "Austrian Science Fund"}', '{"de": "<p>Der Wissenschaftsfonds FWF ist &Ouml;sterreichs f&uuml;hrende Organisation zur themenoffenen F&ouml;rderung der Grundlagenforschung sowie der k&uuml;nstlerisch-wissenschaftlichen Forschung. In einem selektiven, internationalen Peer-Review-Verfahren f&ouml;rdert der FWF jene Forschenden und Ideen, die aufgrund ihrer wissenschaftlichen Qualit&auml;t wegweisend sind. Die gewonnenen Erkenntnisse st&auml;rken &Ouml;sterreich als Forschungsnation und legen eine breite Basis, um zuk&uuml;nftigen gesellschaftlichen Herausforderungen besser begegnen zu k&ouml;nnen. Unabh&auml;ngigkeit und Vielfalt Die gesetzlich verankerte Autonomie des Wissenschaftsfonds FWF gew&auml;hrleistet seine Unabh&auml;ngigkeit und die seiner F&ouml;rdervergabe. Forschende aus allen Wissenschaftsdisziplinen erhalten unabh&auml;ngig von ihrer akademischen Position Freiraum und Zeit, um neue Erkenntnisse gewinnen zu k&ouml;nnen. Exzellenz und Wettbewerb Es ist die wissenschaftliche Qualit&auml;t, die z&auml;hlt. Aus diesem Grund messen sich Forschende im Wettbewerb der Ideen. Der Wissenschaftsfonds FWF investiert ausschlie&szlig;lich in jene Forschenden und ihre Projekte, die sich im internationalen Kontext auf Basis des Peer-Review-Verfahrens als exzellent erweisen. Transparenz und Fairness Der Wissenschaftsfonds FWF setzt auf eine transparente und faire Mittelvergabe. Der Zugang zu seinem F&ouml;rderangebot ist inklusiv gestaltet und orientiert sich an den unterschiedlichen Voraussetzungen der Forschenden. Konsequent beugt er Interessenkonflikten vor und wendet in allen Schritten ein Mehraugenprinzip an. Verfahren und Entscheidungsfindung werden nachvollziehbar kommuniziert. Chancengleichheit und Diversit&auml;t Der FWF f&ouml;rdert die Gleichstellung aller Geschlechter in der Spitzenforschung und setzt auf Gender-Mainstreaming in allen Bereichen. Seine Programme zur Karriereentwicklung unterst&uuml;tzen Forschende auf ihren vielf&auml;ltigen Karrierewegen. Internationale Kooperation Erfolgreiche Wissenschaft basiert auf der Gewinnung von Fakten und Erkenntnissen. Die internationale Kooperation, der freie Zugang zu Wissen (Open Science) und die kritische Reflexion bringen komplement&auml;re Expertisen zusammen und machen Wissenschaft vertrauensw&uuml;rdig. Aus diesem Grund erm&ouml;glicht und f&ouml;rdert der Wissenschaftsfonds FWF Kooperationen &uuml;ber nationale Grenzen hinweg. Integrit&auml;t und Ethik Der Wissenschaftsfonds FWF tr&auml;gt als Gr&uuml;ndungsmitglied der &Ouml;sterreichischen Agentur f&uuml;r wissenschaftliche Integrit&auml;t zur Einhaltung der Regeln guter wissenschaftlicher Praxis und international etablierter ethischer Standards bei. Auch seine eigenen Leistungen sowie die Wirksamkeit seiner F&ouml;rderungen werden regelm&auml;&szlig;ig unabh&auml;ngig evaluiert. Dialog und Kooperation Im Sinne eines Dialogpartners auf Augenh&ouml;he versteht sich der Wissenschaftsfonds FWF als offene B&uuml;hne f&uuml;r den Wissensaustausch. Er schl&auml;gt die Br&uuml;cke zwischen wissenschaftlicher Community, Forschungsinstitutionen, Wirtschaft, Politik, Medien und der &Ouml;ffentlichkeit. Dadurch belebt der FWF die kritische Diskussion zur Rolle der Wissenschaft in einer aufgekl&auml;rten, zukunftsf&auml;higen Gesellschaft. Nachhaltigkeit Der Wissenschaftsfonds FWF achtet in allen Bereichen seiner Arbeit auf klimafreundliche, &ouml;kologische und soziale Nachhaltigkeit. Dar&uuml;ber hinaus setzt sich der FWF f&uuml;r Rahmenbedingungen ein, die es Forschenden erm&ouml;glichen, Forschungsprojekte nachhaltig und klimaschonend durchzuf&uuml;hren.</p>", "en": "<p>Der Wissenschaftsfonds FWF ist &Ouml;sterreichs f&uuml;hrende Organisation zur themenoffenen F&ouml;rderung der Grundlagenforschung sowie der k&uuml;nstlerisch-wissenschaftlichen Forschung. In einem selektiven, internationalen Peer-Review-Verfahren f&ouml;rdert der FWF jene Forschenden und Ideen, die aufgrund ihrer wissenschaftlichen Qualit&auml;t wegweisend sind. Die gewonnenen Erkenntnisse st&auml;rken &Ouml;sterreich als Forschungsnation und legen eine breite Basis, um zuk&uuml;nftigen gesellschaftlichen Herausforderungen besser begegnen zu k&ouml;nnen. Unabh&auml;ngigkeit und Vielfalt Die gesetzlich verankerte Autonomie des Wissenschaftsfonds FWF gew&auml;hrleistet seine Unabh&auml;ngigkeit und die seiner F&ouml;rdervergabe. Forschende aus allen Wissenschaftsdisziplinen erhalten unabh&auml;ngig von ihrer akademischen Position Freiraum und Zeit, um neue Erkenntnisse gewinnen zu k&ouml;nnen. Exzellenz und Wettbewerb Es ist die wissenschaftliche Qualit&auml;t, die z&auml;hlt. Aus diesem Grund messen sich Forschende im Wettbewerb der Ideen. Der Wissenschaftsfonds FWF investiert ausschlie&szlig;lich in jene Forschenden und ihre Projekte, die sich im internationalen Kontext auf Basis des Peer-Review-Verfahrens als exzellent erweisen. Transparenz und Fairness Der Wissenschaftsfonds FWF setzt auf eine transparente und faire Mittelvergabe. Der Zugang zu seinem F&ouml;rderangebot ist inklusiv gestaltet und orientiert sich an den unterschiedlichen Voraussetzungen der Forschenden. Konsequent beugt er Interessenkonflikten vor und wendet in allen Schritten ein Mehraugenprinzip an. Verfahren und Entscheidungsfindung werden nachvollziehbar kommuniziert. Chancengleichheit und Diversit&auml;t Der FWF f&ouml;rdert die Gleichstellung aller Geschlechter in der Spitzenforschung und setzt auf Gender-Mainstreaming in allen Bereichen. Seine Programme zur Karriereentwicklung unterst&uuml;tzen Forschende auf ihren vielf&auml;ltigen Karrierewegen. Internationale Kooperation Erfolgreiche Wissenschaft basiert auf der Gewinnung von Fakten und Erkenntnissen. Die internationale Kooperation, der freie Zugang zu Wissen (Open Science) und die kritische Reflexion bringen komplement&auml;re Expertisen zusammen und machen Wissenschaft vertrauensw&uuml;rdig. Aus diesem Grund erm&ouml;glicht und f&ouml;rdert der Wissenschaftsfonds FWF Kooperationen &uuml;ber nationale Grenzen hinweg. Integrit&auml;t und Ethik Der Wissenschaftsfonds FWF tr&auml;gt als Gr&uuml;ndungsmitglied der &Ouml;sterreichischen Agentur f&uuml;r wissenschaftliche Integrit&auml;t zur Einhaltung der Regeln guter wissenschaftlicher Praxis und international etablierter ethischer Standards bei. Auch seine eigenen Leistungen sowie die Wirksamkeit seiner F&ouml;rderungen werden regelm&auml;&szlig;ig unabh&auml;ngig evaluiert. Dialog und Kooperation Im Sinne eines Dialogpartners auf Augenh&ouml;he versteht sich der Wissenschaftsfonds FWF als offene B&uuml;hne f&uuml;r den Wissensaustausch. Er schl&auml;gt die Br&uuml;cke zwischen wissenschaftlicher Community, Forschungsinstitutionen, Wirtschaft, Politik, Medien und der &Ouml;ffentlichkeit. Dadurch belebt der FWF die kritische Diskussion zur Rolle der Wissenschaft in einer aufgekl&auml;rten, zukunftsf&auml;higen Gesellschaft. Nachhaltigkeit Der Wissenschaftsfonds FWF achtet in allen Bereichen seiner Arbeit auf klimafreundliche, &ouml;kologische und soziale Nachhaltigkeit. Dar&uuml;ber hinaus setzt sich der FWF f&uuml;r Rahmenbedingungen ein, die es Forschenden erm&ouml;glichen, Forschungsprojekte nachhaltig und klimaschonend durchzuf&uuml;hren.</p>"}', '{"de": "Georg-Coch-Platz 2\r\n(Eingang Wiesingerstraße 4)\r\n1010 Wien", "en": "Georg-Coch-Platz 2\r\n(Eingang Wiesingerstraße 4)\r\n1010 Wien"}', 4, NULL, NULL, 'https://www.fwf.ac.at/fileadmin/_processed_/8/5/csm_fwf-logo-blau-rand_bece54b3bf.png', 'https://www.fwf.ac.at/', '{}', '{}', NULL, 'FWF '),
	(43, '{"en": "Radoslav Glińcki"}', '{}', '{}', 2, NULL, NULL, NULL, NULL, '{}', '{}', 0, ''),
	(18, '{"de": "Religiopolitics. Das christliche Imperium & seine Untertanen", "en": "REPLICO"}', '{"de": "<p><strong>REPLICO</strong> ist ein Forschungsprojekt zur Genese und Transformation lokaler Kirchenstrukturen in den Grenzregionen des ottonischen Reiches zwischen dem 10. und 12. Jahrhundert. Im Zentrum steht die Frage, in welcher Weise politische und kirchliche Steuerungsprozesse auf der Ebene der l&auml;ndlichen Bev&ouml;lkerung wirksam wurden und welche Rolle lokale Kirchen in Integrations- und Christianisierungsprozessen spielten.</p>\n<p>Die ottonische Herrschaft (919&ndash;1024) war durch eine kumulative Bedrohungslage an den Peripherien des Reiches charakterisiert. Zeitgen&ouml;ssische Gegner &ndash; Magyaren, slawische Gruppen, Wikinger sowie muslimische Akteure &ndash; stellten die territoriale und politische Koh&auml;renz des Reichs infrage. Die herrschende Forschungslage sieht in der gezielten Gr&uuml;ndung und Ausstattung von Bist&uuml;mern in Grenzregionen ein zentrales Instrument der ottonischen Politik. Diese Bist&uuml;mer fungierten als Knotenpunkte von Mission, Herrschaftsverdichtung und Integration in das Imperium Christianum.</p>\n<p>W&auml;hrend die Rolle der Bist&uuml;mer vergleichsweise gut erforscht ist, sind die Auswirkungen dieser Prozesse auf die l&auml;ndliche Bev&ouml;lkerung bislang deutlich weniger systematisch untersucht worden. <strong>REPLICO</strong> richtet den analytischen Fokus daher auf das sich verdichtende Netz lokaler Kirchen, das den haupts&auml;chlichen Vermittlungsraum zwischen hochrangigen politischen und kirchlichen Strukturen einerseits und der d&ouml;rflichen Bev&ouml;lkerung andererseits bildete.</p>\n<p>Ziel des Projekts ist es, die Entstehung, r&auml;umliche Organisation und funktionale Auspr&auml;gung dieser lokalen Kirchennetze zu rekonstruieren und deren Bedeutung f&uuml;r die Integration slawischer Bev&ouml;lkerungsgruppen in den ottonischen Herrschaftsverband zu bestimmen. Hierzu wird eine umfassende Datenbank arch&auml;ologischer und schriftlicher Quellen f&uuml;r den Raum des heutigen &Ouml;sterreich, Sloweniens und der Tschechischen Republik erstellt, die den Zeitraum vom 10. bis 12. Jahrhundert abdeckt.</p>\n<p>Die Datengrundlage wird mithilfe aktueller geographischer und geostatistischer Analysemethoden sowie unter Einbeziehung maschinellen Lernens ausgewertet. Auf dieser Basis sollen differenzierte Modelle zur Wechselwirkung zwischen politisch-kirchlichen Makrostrukturen und lokalen kirchlichen Mikrostrukturen entwickelt und zu einer neuen historischen Interpretation der Transformationsprozesse in den &ouml;stlichen Grenzr&auml;umen des Reiches zusammengef&uuml;hrt werden.</p>", "en": "<p><strong>REPLICO</strong> ist ein Forschungsprojekt zur Genese und Transformation lokaler Kirchenstrukturen in den Grenzregionen des ottonischen Reiches zwischen dem 10. und 12. Jahrhundert. Im Zentrum steht die Frage, in welcher Weise politische und kirchliche Steuerungsprozesse auf der Ebene der l&auml;ndlichen Bev&ouml;lkerung wirksam wurden und welche Rolle lokale Kirchen in Integrations- und Christianisierungsprozessen spielten.</p>\n<p>Die ottonische Herrschaft (919&ndash;1024) war durch eine kumulative Bedrohungslage an den Peripherien des Reiches charakterisiert. Zeitgen&ouml;ssische Gegner &ndash; Magyaren, slawische Gruppen, Wikinger sowie muslimische Akteure &ndash; stellten die territoriale und politische Koh&auml;renz des Reichs infrage. Die herrschende Forschungslage sieht in der gezielten Gr&uuml;ndung und Ausstattung von Bist&uuml;mern in Grenzregionen ein zentrales Instrument der ottonischen Politik. Diese Bist&uuml;mer fungierten als Knotenpunkte von Mission, Herrschaftsverdichtung und Integration in das Imperium Christianum.</p>\n<p>W&auml;hrend die Rolle der Bist&uuml;mer vergleichsweise gut erforscht ist, sind die Auswirkungen dieser Prozesse auf die l&auml;ndliche Bev&ouml;lkerung bislang deutlich weniger systematisch untersucht worden. <strong>REPLICO</strong> richtet den analytischen Fokus daher auf das sich verdichtende Netz lokaler Kirchen, das den haupts&auml;chlichen Vermittlungsraum zwischen hochrangigen politischen und kirchlichen Strukturen einerseits und der d&ouml;rflichen Bev&ouml;lkerung andererseits bildete.</p>\n<p>Ziel des Projekts ist es, die Entstehung, r&auml;umliche Organisation und funktionale Auspr&auml;gung dieser lokalen Kirchennetze zu rekonstruieren und deren Bedeutung f&uuml;r die Integration slawischer Bev&ouml;lkerungsgruppen in den ottonischen Herrschaftsverband zu bestimmen. Hierzu wird eine umfassende Datenbank arch&auml;ologischer und schriftlicher Quellen f&uuml;r den Raum des heutigen &Ouml;sterreich, Sloweniens und der Tschechischen Republik erstellt, die den Zeitraum vom 10. bis 12. Jahrhundert abdeckt.</p>\n<p>Die Datengrundlage wird mithilfe aktueller geographischer und geostatistischer Analysemethoden sowie unter Einbeziehung maschinellen Lernens ausgewertet. Auf dieser Basis sollen differenzierte Modelle zur Wechselwirkung zwischen politisch-kirchlichen Makrostrukturen und lokalen kirchlichen Mikrostrukturen entwickelt und zu einer neuen historischen Interpretation der Transformationsprozesse in den &ouml;stlichen Grenzr&auml;umen des Reiches zusammengef&uuml;hrt werden.</p>"}', '{}', 1, NULL, NULL, 'https://raw.githubusercontent.com/lisaldrian/Thanados_new_vite/504ba49c60575889c003e1817450012c5ee581ad/images/Replico_Logo.jpg', NULL, '{}', '{}', 198155, 'REPLICO'),
	(39, '{"de": "Slowenische Akademie der Wissenschaften und Künste", "en": "Research Centre of the Slovenian Academy of Sciences and Arts"}', '{"de": "<p>Research Centre of the Slovenian Academy of the Sciences and Arts<br>Novi trg 2, SI-1000 Ljubljana, Slovenia</p>"}', '{"de": "Znanstvenoraziskovalni center\r\nSlovenske akademije znanosti in umetnosti\r\nNovi trg 2\r\nSI-1000 Ljubljana", "en": "Znanstvenoraziskovalni center\r\nSlovenske akademije znanosti in umetnosti\r\nNovi trg 2\r\nSI-1000 Ljubljana"}', 4, NULL, NULL, 'https://uprava.zrc-sazu.si/sites/default/files/inline-images/Logotip%20ZRC%20SAZU.png', 'https://www.zrc-sazu.si/en', '{}', '{}', NULL, 'ZRC SAZU'),
	(45, '{"de": "Karls-Universität", "en": "Charles University"}', '{"de": "<p>Charles University Ovocn&yacute; trh 5 Prague 1 116 36 Czech Republic</p>", "en": "Charles University\n\nOvocný trh 5\n\nPrague 1\n\n116 36\n\nCzech Republic"}', '{"de": "Charles University\r\n\r\nOvocný trh 5\r\n\r\nPrague 1\r\n\r\n116 36\r\n\r\nCzech Republic", "en": "Charles University\r\n\r\nOvocný trh 5\r\n\r\nPrague 1\r\n\r\n116 36\r\n\r\nCzech Republic"}', 4, NULL, NULL, 'https://cuni.cz/UKEN-1-version1-afoto.jpg', 'https://cuni.cz/', '{}', '{}', NULL, 'CUNI'),
	(44, '{"en": "Jan Škvrňák"}', '{}', '{}', 2, 'stefanivos@seznam.cz', '0000-0003-0985-4144', NULL, NULL, '{}', '{}', NULL, ''),
	(59, '{"de": "Universität Tübingen", "en": "University of Tübingen"}', '{}', '{"de": "Eberhard Karls Universität Tübingen\r\nGeschwister-Scholl-Platz\r\n72074 Tübingen", "en": "Eberhard Karls Universität Tübingen\r\nGeschwister-Scholl-Platz\r\n72074 Tübingen"}', 4, NULL, NULL, 'https://uni-tuebingen.de/_assets/7d66ab3e4599366251c5af46f0e770b9/Images/Logo_Universitaet_Tuebingen.svg', NULL, '{}', '{}', NULL, 'EKUT'),
	(40, '{"en": "Ivo Štefan"}', '{}', '{}', 2, NULL, '0000-0003-0752-0036', NULL, NULL, '{}', '{}', 0, ''),
	(41, '{"en": "Dominika Václavíková"}', '{}', '{}', 2, NULL, '0000-0001-9573-0329', NULL, NULL, '{}', '{}', 0, ''),
	(38, '{"en": "Benjamin Štular"}', '{}', '{}', 2, NULL, '0000-0003-1474-7183', NULL, NULL, '{}', '{}', NULL, ''),
	(42, '{"en": "Martin Fajta"}', '{}', '{}', 2, NULL, '0009-0005-6542-8766', NULL, NULL, '{}', '{}', 0, ''),
	(50, '{"en": "Alexander Watzinger "}', '{"en": "<p>... is a software developer with a special interest in data modeling and scientific web applications. Since 2000 he developed software in many different companies before joining the ACDH in 2017. Since 2013 he also acts as the main developer of&nbsp;<a href=\"https://openatlas.eu/\" target=\"_blank\" rel=\"noopener noreferrer\">OpenAtlas</a>, an open source database system for the humanities and beyond. His favorite tools are Python, PostgreSQL, Linux, and open source software in general.</p>\n<p>At the ACDH,&nbsp;Alex leads the Cultural Heritage Artifacts and Context group within the research unit&nbsp;<a href=\"https://www.oeaw.ac.at/acdh/research/dh-research-infrastructure\">DH Research &amp; Infrastructure</a>, where he continues the development of OpenAtlas and coordinates the team and its numerous international collaborations.</p>"}', '{}', 2, 'alexander.watzinger@oeaw.ac.at', NULL, 'https://www.oeaw.ac.at/fileadmin/Institute/ACDH/img/Team/team_watzinger.png', NULL, '{}', '{}', NULL, ''),
	(51, '{"de": "AIS CR Team (Tschechien)", "en": "AIS CR team (Czechia)"}', '{}', '{}', 3, NULL, NULL, NULL, NULL, '{}', '{}', NULL, ''),
	(54, '{"en": "Ondřej Švejcar"}', '{}', '{}', 2, NULL, NULL, NULL, NULL, '{}', '{}', 0, ''),
	(49, '{"de": "Digitalisierung und Übersetzung", "en": "Digitisation and Translations"}', '{}', '{}', 3, NULL, NULL, NULL, NULL, '{}', '{}', NULL, ''),
	(52, '{"en": "Jan Hasil"}', '{}', '{}', 2, NULL, NULL, NULL, NULL, '{}', '{}', 0, ''),
	(53, '{"en": "David Novák"}', '{}', '{}', 2, NULL, NULL, NULL, NULL, '{}', '{}', 0, ''),
	(48, '{"de": "Bioarchäologie", "en": "Bioarchaeology"}', '{}', '{}', 3, NULL, NULL, NULL, NULL, '{}', '{}', NULL, ''),
	(56, '{"de": "Zusätzlicher Support", "en": "Additional Support"}', '{}', '{}', 3, NULL, NULL, NULL, NULL, '{}', '{}', NULL, ''),
	(55, '{"en": "Jan Belik"}', '{}', '{}', 2, NULL, NULL, NULL, NULL, '{}', '{}', 0, ''),
	(35, '{"de": "The Anthropological and Archaeological Database of Sepultures", "en": "The Anthropological and Archaeological Database of Sepultures"}', '{"de": "<p><strong>THANADOS</strong> (The Anthropological and Archaeological Database of Sepultures) befasst sich mit der digitalen Erfassung und Pr&auml;sentation fr&uuml;hmittelalterlicher Gr&auml;berfelder im Gebiet des heutigen &Ouml;sterreichs.</p>\n<p>Im Rahmen von THANADOS wurden bislang ver&ouml;ffentlichte Informationen zu fr&uuml;hmittelalterlichen Bestattungen digitalisiert und ins Englische &uuml;bersetzt. Die Daten sind nach dem <strong>CIDOC CRM</strong> modelliert und online frei zug&auml;nglich. Die Erschlie&szlig;ung erfolgt &uuml;ber einen digitalen Katalog sowie eine interaktive Karte. Kartografische Visualisierungen, Diagramme und statistische Auswertungen werden dynamisch auf Basis realer arch&auml;ologischer Forschungsdaten erzeugt.</p>\n<p>Ziel des Projekts ist es, einen Best-Practice-Ansatz f&uuml;r die zeitgem&auml;&szlig;e Vermittlung arch&auml;ologischer Quellen und Forschung im Kontext der Digital Humanities zu liefern. THANADOS ist eng mit dem <a href=\"https://openatlas.eu/\" target=\"_blank\" rel=\"noopener\">OpenAtlas</a> verbunden und vollst&auml;ndig auf Open-Source-Technologien aufgebaut.</p>\n<p>Das Projekt startete im Juni 2019 und wurde durch das go!digital-NextGeneration-Programm der &Ouml;sterreichische Akademie der Wissenschaften (GDND 2018-039) gef&ouml;rdert. Seit Projektende im Jahr 2021 stellt THANADOS ein Online-Repository aller bislang publizierten fr&uuml;hmittelalterlichen Gr&auml;berfelder im Gebiet des heutigen &Ouml;sterreichs bereit. Das Projekt wird im Rahmen weiterer Kooperationen aktiv fortgef&uuml;hrt, neue Fundstellen werden laufend erg&auml;nzt.</p>\n<p>Die Anwendung ist vollst&auml;ndig Open Source; der Quellcode ist auf GitHub unter der MIT-Lizenz verf&uuml;gbar.</p>", "en": "<p><strong>THANADOS</strong> (The Anthropological and Archaeological Database of Sepultures) deals with the digital collection and presentation of Early Medieval cemeteries in the area of present day Austria. Within THANADOS hitherto published information on Early Medieval burials was digitized and translated to English language. The data are mapped using the CIDOC CRM and provided online. The information can be explored via a digital catalogue and within an interactive map. Cartographic visualisations as well as charts and plots are created dynamically based on real archaeological research data.<br><br>It aims at providing a best practice way on how to disseminate archaeological sources and research in the 21st century against the background of digital humanities. It is closely connected to the <a href=\"https://openatlas.eu/\" target=\"_blank\" rel=\"noopener\">OpenAtlas</a> project and entirely build upon open source technology. It started in June 2019 and is funded by the go!digital NextGeneration programme of the Austrian Academy of Sciences (GDND 2018 039).</p>\n<p>Since the end of the project in 2021 THANADOS provides an online repository of all hitherto published Early Medieval cemeteries from the area of present day Austria. The project is actively carried on within further cooperations and new sites are added continuously The application is entirely open source and the code is available via GitHub under the MIT licence</p>\n<p>&nbsp;</p>"}', '{}', 1, NULL, NULL, 'https://thanados.net/static/images/icons/logo_big.png', 'https://thanados.net/', '{}', '{}', 181731, 'THANADOS'),
	(57, '{"de": "Elias Grünbacher"}', '{"de": "nur der Praktikant"}', '{}', 2, 'eliasgruenbacher@gmail.com', NULL, NULL, NULL, '{}', '{}', 0, ''),
	(58, '{"de": "Österreichische Archäologische Institut ", "en": "Austrian Archaeological Institute"}', '{}', '{"de": "Österreichisches Archäologisches Institut\r\nDominikanerbastei 16\r\n1010 Wien, Österreich\r\n\r\n(Postadresse: Wiesingerstraße 4 | 1010 Wien)", "en": "Austrian Archaeological Institute\r\nDominikanerbastei 16\r\n1010 Vienna, Austria\r\n\r\n(Postal address: Wiesingerstraße 4 | 1010 Vienna)"}', 4, NULL, NULL, 'https://www.oeaw.ac.at/fileadmin/oeaw/institutstemplate/oeai/img/oeai_logo_typ.png', 'https://www.oeaw.ac.at/oeai/', '{}', '{}', NULL, 'ÖAI'),
	(1, '{"de": "THANADOS-Netzwerk", "en": "THANADOS-Network"}', '{"de": "<p><strong>THANADOS-Netzwerk</strong></p>\n<p>Das THANADOS-Netzwerk ist ein offenes Forschungs- und Entwicklungsnetzwerk rund um die Nutzung, Erweiterung und Weiterentwicklung der THANADOS-Datenbasis (The Anthropological and Archaeological Database of Sepultures).</p>\n<p>Ausgehend vom urspr&uuml;nglichen THANADOS-Projekt, das zwischen 2019 und 2021 eine digitale Sammlung fr&uuml;hmittelalterlicher Gr&auml;berfelder im Gebiet des heutigen &Ouml;sterreichs aufbaute, fungiert THANADOS heute als zentrale Daten- und Softwarebasis f&uuml;r weitere Forschungsprojekte, Kooperationen und institutionelle Anwendungen.</p>\n<p>Das Netzwerk umfasst Projekte, die:</p>\n<ul>\n<li>\n<p>auf den bestehenden THANADOS-Daten aufbauen,</p>\n</li>\n<li>\n<p>diese durch neue Fundstellen, Datens&auml;tze oder Auswertungen erweitern,</p>\n</li>\n<li>\n<p>die technische Infrastruktur weiterentwickeln,</p>\n</li>\n<li>\n<p>oder die Daten in neuen wissenschaftlichen, didaktischen oder digitalen Kontexten nutzen.</p>\n</li>\n</ul>\n<p>Die Datenmodellierung basiert auf dem CIDOC CRM, die Inhalte sind &uuml;ber einen digitalen Katalog und eine interaktive Karte zug&auml;nglich. Visualisierungen, Karten und Diagramme werden dynamisch aus realen arch&auml;ologischen Forschungsdaten generiert.</p>\n<p>Die technische Entwicklung erfolgt vollst&auml;ndig Open Source. Der Quellcode wird gemeinschaftlich &uuml;ber GitHub gepflegt und steht unter der MIT-Lizenz zur Verf&uuml;gung. Das THANADOS Network versteht sich damit als langfristige, offene Infrastruktur im Schnittfeld von Arch&auml;ologie und Digital Humanities.</p>", "en": "<p><strong>THANADOS-Network</strong></p>\n<p>The THANADOS-Network is an open research and development network focused on the use, extension, and continued development of the THANADOS data infrastructure (The Anthropological and Archaeological Database of Sepultures).</p>\n<p>Building on the original THANADOS project, which between 2019 and 2021 established a digital collection of Early Medieval cemeteries in the area of present-day Austria, THANADOS now serves as a central data and software foundation for further research projects, collaborations, and institutional applications.</p>\n<p>The network brings together projects that:</p>\n<ul>\n<li>\n<p>build upon existing THANADOS data,</p>\n</li>\n<li>\n<p>extend the dataset through new sites, records, or analyses,</p>\n</li>\n<li>\n<p>further develop the technical infrastructure,</p>\n</li>\n<li>\n<p>or reuse the data in new scholarly, educational, or digital contexts.</p>\n</li>\n</ul>\n<p>Data modelling is based on CIDOC CRM. The information is accessible through a digital catalogue and an interactive map. Cartographic visualisations, charts, and plots are generated dynamically from real archaeological research data.</p>\n<p>All technical development is carried out entirely as open source. The source code is collaboratively maintained via GitHub and released under the MIT License. The THANADOS Network is conceived as a long-term, open infrastructure at the intersection of archaeology and digital humanities.</p>"}', '{}', 5, NULL, NULL, '/static/images/logos/logo_mode_light.svg', NULL, '{"de": "<p>Die Erstellung, die Verwendung und die nicht kommerzielle Weitergabe von Kopien&nbsp;in elektronischer oder ausgedruckter Form sind erlaubt, wenn der Inhalt nicht entstellt&nbsp;und die Quelle angegeben wird (Quelle: NHM Wien). Texte, Bilder und Grafiken unterliegen&nbsp;dem Schutz des Urheberrechts und anderer Schutzgesetze, soweit nicht anders angegeben.<br>Trotz gr&ouml;&szlig;tm&ouml;glicher Sorgfalt bei der Erstellung dieser Website kann das NHM Wien nicht&nbsp;die Fehlerfreiheit und Genauigkeit der enthaltenen Informationen garantieren.&nbsp;Das NHM Wien schlie&szlig;t jegliche Haftung f&uuml;r Sch&auml;den, die direkt oder indirekt aus der&nbsp;Benutzung der Website entstehen, aus.</p>", "en": "<p>The creation, use, and non-commercial distribution of copies in<br>electronic or printed form are permitted, provided that the content is<br>not distorted and the source is acknowledged (source: NHM Vienna).<br>Texts, images, and graphics are protected by copyright and other<br>protective laws, unless otherwise indicated. Despite the greatest<br>possible care in the preparation of this website, the NHM Vienna cannot<br>guarantee the absence of errors or the accuracy of the information<br>contained therein. The NHM Vienna excludes all liability for damages<br>arising directly or indirectly from the use of the website.</p>"}', '{"de": "<p><strong>THANADOS &ndash; The Anthropological and Archaeological Database of Sepultures</strong></p>\n<p>Betreut von:<br>Naturhistorisches Museum Wien (NHM Wien), Abteilung Pr&auml;historie<br>&amp; &Ouml;sterreichisches Arch&auml;ologisches Institut (&Ouml;AI) / &Ouml;sterreichische Akademie der Wissenschaften (&Ouml;AW)</p>\n<p><strong>Kontakt:<br></strong><strong>Naturhistorisches Museum Wien (&Ouml;)</strong><br>Kontaktperson: Mag. Dr. Stefan Eichert<br>E-Mail: <a rel=\"noopener\">stefan.eichert@nhm-wien.ac.at</a><br>Adresse: Burgring 7, 1010 Wien, &Ouml;sterreich</p>\n<p><strong>&Ouml;sterreichisches Arch&auml;ologisches Institut (&Ouml;AI / &Ouml;AW)</strong><br>Kontaktperson: Nina Richards, MA BSc<br>E-Mail: <a rel=\"noopener\">nina.richards@oeaw.ac.at</a><br>Adresse: Rosenbursenstra&szlig;e 3, 1010 Wien, &Ouml;sterreich</p>\n<p><strong>Institut f&uuml;r Arch&auml;ologie der Tschechischen Akademie der Wissenschaften, Prag (CZ)</strong><br>Kontaktperson: Mgr. David Nov&aacute;k, Ph.D.<br>E-Mail: <a rel=\"noopener\">novak@arup.cas.cz</a><br>Adresse: Letensk&aacute; 123/4, 118 01 Prag 1, Tschechien</p>\n<p>Die von THANADOS bereitgestellten Daten stehen unter der<br>Creative-Commons-Lizenz Namensnennung 4.0 International (CC BY 4.0).<br>Die Software selbst wird unter der<br>MIT-Lizenz ver&ouml;ffentlicht.</p>", "en": "<p><strong>THANADOS &ndash; The Anthropological and Archaeological Database of Sepultures</strong><br><br>Hosted by:<br>Natural History Museum Vienna (NHM Vienna), Department of Prehistory&nbsp;<br>&amp; Austrian Archaeological Institute (&Ouml;AI) / Austrian Academy of Sciences (&Ouml;AW)</p>\n<p><strong>Contact:<br></strong><strong>Natural History Museum Vienna (AUT)<br></strong>Contact person: Mag. Dr. Stefan Eichert<br>E-mail: stefan.eichert@nhm-wien.ac.at<br>Address: Burgring 7, 1010 Vienna, Austria<br><br></p>\n<p><strong>Austrian Archaeological Institute (&Ouml;AI / &Ouml;AW)</strong><br>Contact person: Nina Richards, MA BSc<br>E-mail: nina.richards@oeaw.ac.at<br>Address: Rosenbursenstra&szlig;e 3, 1010 Vienna, Austria</p>\n<p><br><strong>Institute of Archaeology of the Czech Academy of Sciences, Prague (CZ)</strong><br>Contact person: Mgr. David Nov&aacute;k, Ph.D.<br>E-mail: novak@arup.cas.cz<br>Address: Letensk&aacute; 123/4, 118 01 Prague 1, Czechia</p>\n<p>The data provided by THANADOS are licensed under the&nbsp;<br><a href=\"https://creativecommons.org/licenses/by/4.0/\">Creative Commons Attribution 4.0 International License (CC BY 4.0)</a>.<br>The software itself is released under the&nbsp;<br><a href=\"https://opensource.org/licenses/MIT\">MIT License</a>.</p>\n<p>&nbsp;</p>"}', NULL, 'THANADOS-Netzwerk'),
	(33, '{"de": "Bernhard Koschiček-Krombholz", "en": "Bernhard Koschicek-Krombholz"}', '{"de": "<p>... erwarb seinen Bachelor of Science in Informatik an der Fachhochschule Technikum Wien und seinen Bachelor of Arts in Geschichte an der Universit&auml;t Wien. Seit 2015 ist er am Institut f&uuml;r Mittelalterforschung der &Ouml;sterreichischen Akademie der Wissenschaften und seit 2017 am <a href=\"https://www.oeaw.ac.at/acdh/\" target=\"_blank\" rel=\"noopener\"><strong>ACDH</strong></a> t&auml;tig. Seine Interessensgebiete umfassen mittelalterliche Geschichte, insbesondere Osteuropa, historische Geographie, GIS, API-Entwicklung und Python.</p>", "en": "... received his BSc in Computer Science from the University of Applied Sciences Technikum Wien and his BA in History from the University of Vienna. He has been working at the Institute for Medieval Studies at the Austrian Academy of Sciences since 2015 and at ACDH since 2017. His interests are medieval history, especially Eastern Europe, historical geography, GIS, API development and Python."}', '{}', 2, 'Bernhard.Koschicek@oeaw.ac.at', '0000-0001-7608-7446', 'https://www.oeaw.ac.at/fileadmin/_processed_/8/d/csm_team_koschicek_acf8d10c9b.png', NULL, '{}', '{}', NULL, '');


--
-- Data for Name: links; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

INSERT INTO tng.links OVERRIDING SYSTEM VALUE VALUES
	(3, 22, 21, 2, 5, 3),
	(5, 18, 22, 1, 5, 5),
	(11, 4, 19, 2, 10, 11),
	(12, 18, 4, 1, 13, 12),
	(13, 17, 4, 1, 10, 13),
	(15, 2, 19, 2, 5, 15),
	(16, 2, 19, 2, 10, 16),
	(17, 2, 19, 2, 8, 17),
	(21, 4, 20, 2, 13, 21),
	(33, 18, 20, 5, 15, 29),
	(34, 17, 2, 1, 5, 30),
	(42, 35, 2, 1, 5, 38),
	(43, 35, 2, 1, 6, 39),
	(44, 35, 22, 1, 5, 40),
	(45, 35, 33, 1, 8, 41),
	(46, 35, 19, 5, 34, 42),
	(48, 17, 19, 5, 34, 44),
	(49, 17, 36, 5, 14, 45),
	(50, 17, 22, 1, 10, 46),
	(51, 17, 22, 1, 11, 47),
	(52, 17, 33, 1, 9, 48),
	(53, 17, 3, 1, 9, 49),
	(54, 17, 3, 1, 12, 50),
	(55, 17, 4, 1, 12, 51),
	(56, 3, 19, 2, 9, 52),
	(57, 18, 2, 1, 5, 53),
	(58, 18, 3, 1, 9, 54),
	(59, 18, 33, 1, 9, 55),
	(60, 18, 3, 1, 12, 56),
	(61, 17, 37, 1, 10, 57),
	(63, 18, 38, 1, 5, 58),
	(64, 18, 40, 1, 10, 59),
	(65, 18, 41, 1, 10, 60),
	(66, 18, 42, 1, 10, 61),
	(67, 18, 43, 1, 10, 62),
	(69, 18, 39, 5, 15, 63),
	(70, 18, 45, 5, 15, 64),
	(71, 35, 2, 1, 9, 65),
	(72, 35, 22, 1, 48, 66),
	(73, 50, 21, 2, 8, 67),
	(74, 35, 52, 1, 51, 68),
	(75, 35, 53, 1, 51, 69),
	(76, 35, 54, 1, 51, 70),
	(77, 35, 50, 1, 8, 71),
	(78, 35, 21, 5, 15, 72),
	(80, 35, 55, 1, 56, 73),
	(82, 17, 57, 1, NULL, 74),
	(87, 35, 58, 5, 15, 79),
	(37, 1, 2, 3, 6, 1),
	(39, 1, 33, 3, 8, 2),
	(40, 1, 19, 4, NULL, 3),
	(41, 1, 19, 4, 34, 4),
	(83, 1, 3, 3, 9, 5),
	(84, 1, 2, 3, 9, 6),
	(85, 1, 57, 3, 9, 7),
	(86, 1, 22, 3, NULL, 8);


--
-- Data for Name: maps; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

INSERT INTO tng.maps VALUES
	(1, 'OpenStreetMap', 'Open Street Map', 'https://api.maptiler.com/maps/bright/style.json?key=E7Jrgaazm79UlTuEI5f5', 1);


--
-- Data for Name: properties; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

INSERT INTO tng.properties OVERRIDING SYSTEM VALUE VALUES
	(1, '{"de": "hat Mitglied", "en": "has member"}', '{"de": "ist Mitglied von", "en": "is member of"}', 1, 2),
	(2, '{"de": "hat Zugehörigkeit", "en": "has affiliation"}', '{"de": "ist Zugehörigkeit von", "en": "is affiliation of"}', 2, 4),
	(3, '{"de": "hat Kernmitglied", "en": "has core member"}', '{"de": "ist Kernmitglied von", "en": "is core member of"}', 5, 2),
	(4, '{"de": "hat Kerninstitution", "en": "has core institution"}', '{"de": "ist Kerninstitution von", "en": "is core institution of"}', 5, 4),
	(5, '{"de": "hat Institution", "en": "has institution"}', '{"de": "ist Institution von", "en": "is institution of"}', 1, 4);


--
-- Data for Name: settings; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

INSERT INTO tng.settings VALUES
	(1, '/static/images/index_map_bg/Blank_map_of_Europe_central_network.png', 1, 'map', false, '{place,feature,stratigraphic_unit,artifact,human_remains,person,group,acquisition,event,activity,creation,move,production,modification}', NULL, '{group}', NULL, NULL, NULL, 8240);


--
-- Name: classes_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.classes_id_seq', 1, false);


--
-- Name: entities_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.entities_id_seq', 59, true);


--
-- Name: links_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.links_id_seq', 29, true);


--
-- Name: links_id_seq1; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.links_id_seq1', 88, true);


--
-- Name: maps_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.maps_id_seq', 1, true);


--
-- Name: properties_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.properties_id_seq', 1, false);


--
-- Name: settings_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.settings_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

\unrestrict K5X8QF25Wg1QgD8OLPhHrApTdcpAtvNgDEQCqg3idMwy1oYp9B8oyAPvtAM003T

