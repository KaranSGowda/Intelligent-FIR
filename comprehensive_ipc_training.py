"""
Comprehensive training dataset covering all major IPC sections.
This file contains training examples for all important IPC sections.
"""

# List of all major IPC sections to be covered
MAJOR_IPC_SECTIONS = [
    # Against the State
    "121", "121A", "122", "123", "124", "124A", "125", "126", "127", "128", "129", "130",
    
    # Against Public Justice
    "191", "192", "193", "194", "195", "196", "197", "198", "199", "200", "201", "202", "203", "204", "205", "206", "207", "208", "209", "210", "211", "212", "213", "214", "215", "216", "217", "218", "219", "220", "221", "222", "223", "224", "225", "226", "227", "228", "229",
    
    # Against Public Tranquility
    "141", "142", "143", "144", "145", "146", "147", "148", "149", "150", "151", "152", "153", "153A", "153B", "154", "155", "156", "157", "158", "159", "160",
    
    # Against Human Body
    "299", "300", "301", "302", "303", "304", "304A", "304B", "305", "306", "307", "308", "309", "310", "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "321", "322", "323", "324", "325", "326", "326A", "326B", "327", "328", "329", "330", "331", "332", "333", "334", "335", "336", "337", "338",
    
    # Wrongful Restraint and Confinement
    "339", "340", "341", "342", "343", "344", "345", "346", "347", "348",
    
    # Criminal Force and Assault
    "349", "350", "351", "352", "353", "354", "354A", "354B", "354C", "354D", "355", "356", "357", "358",
    
    # Kidnapping and Abduction
    "359", "360", "361", "362", "363", "363A", "364", "364A", "365", "366", "366A", "366B", "367", "368", "369",
    
    # Sexual Offenses
    "375", "376", "376A", "376B", "376C", "376D", "376E", "377",
    
    # Theft
    "378", "379", "380", "381", "382",
    
    # Extortion
    "383", "384", "385", "386", "387", "388", "389",
    
    # Robbery and Dacoity
    "390", "391", "392", "393", "394", "395", "396", "397", "398", "399", "400", "401", "402",
    
    # Criminal Misappropriation
    "403", "404",
    
    # Criminal Breach of Trust
    "405", "406", "407", "408", "409",
    
    # Receiving Stolen Property
    "410", "411", "412", "413", "414",
    
    # Cheating
    "415", "416", "417", "418", "419", "420", "421", "422", "423", "424",
    
    # Mischief
    "425", "426", "427", "428", "429", "430", "431", "432", "433", "434", "435", "436", "437", "438", "439", "440",
    
    # Criminal Trespass
    "441", "442", "443", "444", "445", "446", "447", "448", "449", "450", "451", "452", "453", "454", "455", "456", "457", "458", "459", "460",
    
    # Forgery
    "463", "464", "465", "466", "467", "468", "469", "470", "471", "472", "473", "474", "475", "476", "477", "477A",
    
    # Defamation
    "499", "500", "501", "502",
    
    # Criminal Intimidation
    "503", "504", "505", "506", "507", "508", "509", "510",
    
    # IT Act Sections
    "66", "66A", "66B", "66C", "66D", "66E", "66F", "67", "67A", "67B", "68", "69", "70", "71", "72", "73", "74", "75"
]

# Comprehensive training dataset
COMPREHENSIVE_TRAINING_CASES = [
    # Against the State (Sections 121-130)
    ("The accused was involved in waging war against the Government of India by organizing armed rebellion.", ["121"]),
    ("The accused conspired to commit offenses punishable under section 121 by planning an armed uprising.", ["121A"]),
    ("The accused collected weapons with the intention of waging war against the Government of India.", ["122"]),
    ("The accused concealed information about a planned rebellion against the Government of India.", ["123"]),
    ("The accused assaulted the President with intent to compel him to exercise his lawful powers.", ["124"]),
    ("The accused made seditious statements against the Government to incite disaffection and rebellion.", ["124A"]),
    ("The accused waged war against an Asian country that has an alliance with India.", ["125"]),
    ("The accused committed depredation on territories of a country at peace with India.", ["126"]),
    ("The accused received property taken during war with a country at peace with India.", ["127"]),
    ("The accused, a public servant, voluntarily allowed a prisoner of state to escape from custody.", ["128"]),
    ("The accused, a public servant, negligently allowed a prisoner of state to escape from custody.", ["129"]),
    ("The accused aided the escape of a prisoner of state and harbored them after the escape.", ["130"]),

    # Public Justice (Sections 191-229) - Selected important ones
    ("The accused gave false evidence in a judicial proceeding by lying under oath.", ["191", "193"]),
    ("The accused fabricated false evidence to be used in a court proceeding.", ["192", "193"]),
    ("The accused destroyed evidence of a crime to shield the offender from legal punishment.", ["201"]),
    ("The accused knowingly harbored an offender who had committed a serious crime.", ["212"]),
    ("The accused took a gift to help a person recover stolen property without reporting to police.", ["214"]),
    ("The accused, a public servant, disobeyed the law with intent to cause injury to another person.", ["217"]),
    ("The accused filed a false charge of an offense against another person, knowing it to be false.", ["211"]),

    # Public Tranquility (Sections 141-160)
    ("The accused was a member of an unlawful assembly of five or more persons.", ["143"]),
    ("The accused joined an unlawful assembly armed with a deadly weapon.", ["144"]),
    ("The accused participated in a riot by using force and violence as part of an unlawful assembly.", ["147"]),
    ("The accused participated in a riot while armed with a deadly weapon.", ["148"]),
    ("The accused hired people to join an unlawful assembly.", ["150"]),
    ("The accused promoted enmity between different religious groups through hateful speeches.", ["153A"]),
    ("The accused made assertions prejudicial to national integration based on religion and region.", ["153B"]),
    ("The accused engaged in an affray by fighting in a public place, disturbing public peace.", ["160"]),

    # Against Human Body - Murder, Culpable Homicide (Sections 299-311)
    ("The accused murdered the victim by stabbing him multiple times with premeditation.", ["302"]),
    ("The accused caused death by negligence when driving recklessly, resulting in a fatal accident.", ["304A"]),
    ("The accused's actions led to the death of his wife within seven years of marriage related to dowry.", ["304B"]),
    ("The accused abetted the suicide of the victim by constantly harassing and humiliating them.", ["306"]),
    ("The accused attempted to murder the victim by poisoning their food, but the victim survived.", ["307"]),
    ("The accused attempted to commit culpable homicide by attacking the victim with a blunt object.", ["308"]),
    ("The accused attempted suicide by consuming poison after facing financial difficulties.", ["309"]),

    # Against Human Body - Hurt (Sections 319-338)
    ("The accused voluntarily caused hurt to the victim by punching and slapping them.", ["323"]),
    ("The accused caused hurt using a dangerous weapon by attacking the victim with a knife.", ["324"]),
    ("The accused caused grievous hurt by breaking the victim's arm during an assault.", ["325"]),
    ("The accused caused grievous hurt using a dangerous weapon by attacking with an iron rod.", ["326"]),
    ("The accused threw acid on the victim causing permanent disfigurement and damage.", ["326A"]),
    ("The accused attempted to throw acid on the victim but was stopped before causing harm.", ["326B"]),
    ("The accused administered a stupefying drug to the victim to commit theft.", ["328"]),
    ("The accused performed a rash act endangering human life by driving at high speed in a crowded area.", ["336"]),
    ("The accused caused hurt by a rash and negligent act that endangered human life.", ["337"]),
    ("The accused caused grievous hurt by a rash and negligent act that endangered human life.", ["338"]),

    # Wrongful Restraint and Confinement (Sections 339-348)
    ("The accused wrongfully restrained the victim by preventing them from proceeding in a direction.", ["341"]),
    ("The accused wrongfully confined the victim by detaining them in a room against their will.", ["342"]),
    ("The accused wrongfully confined the victim for more than three days.", ["343"]),
    ("The accused wrongfully confined the victim for more than ten days.", ["344"]),
    ("The accused wrongfully confined the victim in secret, hiding their whereabouts from family.", ["346"]),

    # Criminal Force and Assault (Sections 349-358)
    ("The accused used criminal force against the victim by pushing them without consent.", ["352"]),
    ("The accused assaulted a public servant while they were performing their official duties.", ["353"]),
    ("The accused assaulted a woman with intent to outrage her modesty by inappropriately touching her.", ["354"]),
    ("The accused sexually harassed the victim by making unwelcome sexual advances and remarks.", ["354A"]),
    ("The accused assaulted a woman with intent to disrobe her by forcibly pulling at her clothes.", ["354B"]),
    ("The accused engaged in voyeurism by secretly recording a woman in a private act.", ["354C"]),
    ("The accused stalked a woman by repeatedly following her and monitoring her online activities.", ["354D"]),

    # Kidnapping and Abduction (Sections 359-369)
    ("The accused kidnapped a minor child from lawful guardianship without the guardian's consent.", ["363"]),
    ("The accused kidnapped a minor for the purpose of begging, forcing them to seek alms.", ["363A"]),
    ("The accused kidnapped a person with the intent to murder them.", ["364"]),
    ("The accused kidnapped a person for ransom, threatening to kill them if demands weren't met.", ["364A"]),
    ("The accused kidnapped a person with the intent to secretly and wrongfully confine them.", ["365"]),
    ("The accused kidnapped a woman to compel her into marriage against her will.", ["366"]),
    ("The accused procured a minor girl for illicit intercourse with another person.", ["366A"]),
    ("The accused imported a girl from a foreign country for illicit intercourse.", ["366B"]),
    ("The accused kidnapped a person to subject them to grievous hurt or slavery.", ["367"]),

    # Sexual Offenses (Sections 375-377)
    ("The accused committed rape by having sexual intercourse with the victim without her consent.", ["376"]),
    ("The accused caused the death of the victim during rape, resulting in her death.", ["376A"]),
    ("The accused, a husband, had sexual intercourse with his wife during separation without consent.", ["376B"]),
    ("The accused, a person in authority, abused his position to have sexual intercourse with a woman.", ["376C"]),
    ("The accused along with others committed gang rape of the victim.", ["376D"]),
    ("The accused, previously convicted of rape, committed rape again.", ["376E"]),
    ("The accused committed carnal intercourse against the order of nature without consent.", ["377"]),

    # Theft (Sections 378-382)
    ("The accused committed theft by dishonestly taking the victim's mobile phone from their pocket.", ["379"]),
    ("The accused committed theft in a dwelling house by stealing valuables from the victim's home.", ["380"]),
    ("The accused, a domestic servant, committed theft of jewelry from the employer's house.", ["381"]),
    ("The accused committed theft after preparation to cause death or hurt to enable the theft.", ["382"]),

    # Extortion (Sections 383-389)
    ("The accused committed extortion by threatening to harm the victim if they didn't pay money.", ["384"]),
    ("The accused put the victim in fear of injury to extort money from them.", ["385"]),
    ("The accused put the victim in fear of death to extort money from them.", ["386"]),
    ("The accused attempted to extort money by threatening to accuse the victim of a serious crime.", ["388"]),

    # Robbery and Dacoity (Sections 390-402)
    ("The accused committed robbery by using force to steal the victim's wallet and phone.", ["392"]),
    ("The accused attempted to commit robbery but was caught before completing the act.", ["393"]),
    ("The accused caused hurt while committing robbery by hitting the victim with a blunt object.", ["394"]),
    ("The accused, along with four others, committed dacoity by robbing a bank at gunpoint.", ["395"]),
    ("The accused committed murder during a dacoity operation.", ["396"]),
    ("The accused used a deadly weapon while committing robbery, threatening the victim with a knife.", ["397"]),
    ("The accused made preparations to commit dacoity by gathering weapons and planning the attack.", ["399"]),
    ("The accused belonged to a gang of persons associated for the purpose of habitual robbery.", ["401"]),

    # Criminal Misappropriation (Sections 403-404)
    ("The accused dishonestly misappropriated property that was entrusted to him for safekeeping.", ["403"]),
    ("The accused dishonestly misappropriated property belonging to a deceased person.", ["404"]),

    # Criminal Breach of Trust (Sections 405-409)
    ("The accused committed criminal breach of trust by misappropriating funds entrusted to him.", ["406"]),
    ("The accused, a carrier, committed criminal breach of trust with goods entrusted for transport.", ["407"]),
    ("The accused, a clerk, committed criminal breach of trust with funds from his employer.", ["408"]),
    ("The accused, a public servant, committed criminal breach of trust with government funds.", ["409"]),

    # Receiving Stolen Property (Sections 410-414)
    ("The accused dishonestly received stolen property knowing it to be stolen.", ["411"]),
    ("The accused dishonestly received property stolen in a dacoity, knowing it was stolen.", ["412"]),
    ("The accused habitually dealt in stolen property as part of his business.", ["413"]),
    ("The accused assisted in concealing stolen property to prevent its recovery.", ["414"]),

    # Cheating (Sections 415-424)
    ("The accused cheated the victim by dishonestly inducing them to deliver money for a fake job.", ["420"]),
    ("The accused cheated by personation, pretending to be someone else to obtain property.", ["419"]),
    ("The accused dishonestly concealed property to prevent distribution among creditors.", ["421"]),
    ("The accused dishonestly executed a deed of transfer containing a false statement.", ["423"]),

    # Mischief (Sections 425-440)
    ("The accused committed mischief by damaging the victim's car, causing loss of Rs. 50,000.", ["427"]),
    ("The accused committed mischief by killing the victim's pet dog out of spite.", ["428"]),
    ("The accused committed mischief by damaging public irrigation works, affecting farmers.", ["430"]),
    ("The accused committed mischief by fire, burning down the victim's shop.", ["435"]),
    ("The accused committed mischief by fire with intent to destroy a house.", ["436"]),

    # Criminal Trespass (Sections 441-460)
    ("The accused committed criminal trespass by entering the victim's property without permission.", ["447"]),
    ("The accused committed house trespass by entering the victim's house without permission.", ["448"]),
    ("The accused committed house trespass to commit an offense of theft inside the house.", ["451"]),
    ("The accused committed lurking house trespass by night, entering the house after sunset.", ["456"]),
    ("The accused committed house-breaking by entering through a window not meant for entry.", ["445"]),
    ("The accused committed house-breaking by night to commit theft inside the house.", ["457"]),

    # Forgery (Sections 463-477A)
    ("The accused committed forgery by creating a false document to claim ownership of property.", ["465"]),
    ("The accused committed forgery of a valuable security like a check to obtain money.", ["467"]),
    ("The accused committed forgery for the purpose of cheating, creating fake investment documents.", ["468"]),
    ("The accused committed forgery to harm the reputation of another person.", ["469"]),
    ("The accused used a forged document as genuine, knowing it to be forged.", ["471"]),

    # Defamation (Sections 499-502)
    ("The accused defamed the victim by making false statements about their character.", ["499", "500"]),
    ("The accused printed defamatory content about the victim in a newspaper.", ["501"]),
    ("The accused sold printed defamatory content knowing it contained defamatory matter.", ["502"]),

    # Criminal Intimidation (Sections 503-510)
    ("The accused criminally intimidated the victim by threatening to harm them.", ["506"]),
    ("The accused intentionally insulted the victim to provoke a breach of peace.", ["504"]),
    ("The accused made statements conducing to public mischief, causing fear in the community.", ["505"]),
    ("The accused criminally intimidated the victim through anonymous communication.", ["507"]),
    ("The accused insulted the modesty of a woman by making lewd gestures and comments.", ["509"]),
    ("The accused, while drunk, created a public nuisance in a public place.", ["510"]),

    # IT Act Sections (Sections 66-75)
    ("The accused hacked into the victim's computer system and stole sensitive data.", ["66"]),
    ("The accused sent threatening and abusive messages to the victim through electronic means.", ["66A"]),
    ("The accused dishonestly received stolen computer resources or communication devices.", ["66B"]),
    ("The accused stole the victim's digital identity by fraudulently using their password.", ["66C"]),
    ("The accused cheated by personation using a computer resource or communication device.", ["66D"]),
    ("The accused violated the privacy of the victim by capturing and publishing private images.", ["66E"]),
    ("The accused committed cyber terrorism by accessing a protected computer system.", ["66F"]),
    ("The accused published obscene material in electronic form on a social media platform.", ["67"]),
    ("The accused published sexually explicit material in electronic form.", ["67A"]),
    ("The accused published child pornography in electronic form.", ["67B"])
]

# Additional cases with variations to improve model training
ADDITIONAL_VARIATIONS = [
    # Murder variations
    ("The accused killed the victim by shooting them with a gun during a robbery.", ["302"]),
    ("The accused murdered the victim by poisoning their food over a property dispute.", ["302"]),
    ("The accused strangled the victim to death following an argument.", ["302"]),
    
    # Theft variations
    ("Someone stole my phone while I was traveling on the bus yesterday.", ["379"]),
    ("My laptop was stolen from my office desk when I went for lunch.", ["379"]),
    ("The accused pickpocketed my wallet at the crowded market.", ["379"]),
    
    # Assault variations
    ("I was beaten by a group of people outside the restaurant last night.", ["323"]),
    ("The accused hit me with his fists causing bruises on my face.", ["323"]),
    ("The accused assaulted me with a wooden stick causing injuries.", ["324"]),
    
    # Rape variations
    ("The victim was sexually assaulted by the accused in his apartment.", ["376"]),
    ("The accused forcibly raped the victim against her consent.", ["376"]),
    ("The victim was drugged and then raped by the accused.", ["376"]),
    
    # Cheating variations
    ("I invested Rs. 5 lakhs in a fake company based on false promises of high returns.", ["420"]),
    ("The accused sold me counterfeit products claiming them to be genuine branded items.", ["420"]),
    ("The accused took an advance payment for services but never delivered them.", ["420"]),
    
    # Criminal intimidation variations
    ("The accused threatened to kill me if I reported the matter to the police.", ["506"]),
    ("I received death threats from the accused after I filed a complaint against him.", ["506"]),
    ("The accused threatened to harm my family if I didn't withdraw the case.", ["506"]),
    
    # Dowry harassment variations
    ("My husband and in-laws have been harassing me for additional dowry since marriage.", ["498A"]),
    ("I've been subjected to cruelty by my husband and his family for not bringing enough dowry.", ["498A"]),
    ("My in-laws physically and mentally tortured me for dowry.", ["498A"]),
    
    # Stalking variations
    ("The accused has been following me to my workplace and home for the past month.", ["354D"]),
    ("I'm being stalked by the accused who keeps sending unwanted messages despite my refusal.", ["354D"]),
    ("The accused monitors my social media and appears wherever I go.", ["354D"]),
    
    # Forgery variations
    ("The accused forged my signature on bank documents to withdraw money from my account.", ["465", "468"]),
    ("My tenant created a fake rental agreement with forged signatures.", ["465"]),
    ("The accused created counterfeit identity documents using my personal information.", ["465", "468"]),
    
    # Robbery variations
    ("The accused robbed me at knifepoint and took my wallet and phone.", ["392"]),
    ("I was threatened with a gun during a robbery at my shop.", ["392", "397"]),
    ("The accused snatched my gold chain using force while I was walking.", ["392"])
]

# Combine all training cases
ALL_TRAINING_CASES = COMPREHENSIVE_TRAINING_CASES + ADDITIONAL_VARIATIONS
