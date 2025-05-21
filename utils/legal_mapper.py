"""
This module provides functionality to map legal sections to complaints
based on the content of the complaint.
"""

import json
import os
from models import LegalSection
from extensions import db

def initialize_legal_sections():
    """
    Initialize the database with common Indian Penal Code sections.
    This function should be called only once when setting up the application.
    """
    # Check if sections already exist
    if LegalSection.query.count() > 0:
        return

    # Comprehensive list of IPC sections relevant to FIRs
    sections = [
        # General Explanations and Basic Principles (1-52)
        {"code": "1", "name": "Title and extent of operation of the Code", "description": "This Act shall be called the Indian Penal Code, and shall extend to the whole of India"},
        {"code": "2", "name": "Punishment of offences committed within India", "description": "Every person shall be liable to punishment under this Code for every act or omission contrary to the provisions thereof, of which he shall be guilty within India"},
        {"code": "3", "name": "Punishment of offences committed beyond, but which by law may be tried within, India", "description": "Any person liable to be tried for an offence committed beyond India shall be dealt with according to the provisions of this Code"},
        {"code": "4", "name": "Extension of Code to extra-territorial offences", "description": "The provisions of this Code apply to any offence committed by any citizen of India in any place without and beyond India"},
        {"code": "5", "name": "Certain laws not to be affected by this Act", "description": "Nothing in this Act shall affect the provisions of any Act for punishing mutiny and desertion of officers, soldiers, sailors or airmen in the service of the Government of India"},

        # General Exceptions (76-106)
        {"code": "76", "name": "Act done by a person bound by law", "description": "Nothing is an offence which is done by a person who is bound by law to do it"},
        {"code": "77", "name": "Act of Judge when acting judicially", "description": "Nothing is an offence which is done by a Judge when acting judicially in the exercise of any power which is given to him by law"},
        {"code": "78", "name": "Act done pursuant to the judgment or order of Court", "description": "Nothing which is done in pursuance of, or which is warranted by the judgment or order of, a Court of Justice"},
        {"code": "79", "name": "Act done by a person justified by law", "description": "Nothing is an offence which is done by any person who is justified by law in doing it"},
        {"code": "80", "name": "Accident in doing a lawful act", "description": "Nothing is an offence which is done by accident or misfortune, and without any criminal intention or knowledge"},
        {"code": "81", "name": "Act likely to cause harm, but done without criminal intent", "description": "Nothing is an offence merely by reason of its being done with the knowledge that it is likely to cause harm"},
        {"code": "82", "name": "Act of a child under seven years of age", "description": "Nothing is an offence which is done by a child under seven years of age"},
        {"code": "83", "name": "Act of a child above seven and under twelve", "description": "Nothing is an offence which is done by a child above seven years of age and under twelve, who has not attained sufficient maturity of understanding"},
        {"code": "84", "name": "Act of a person of unsound mind", "description": "Nothing is an offence which is done by a person who, at the time of doing it, is incapable of knowing the nature of the act"},
        {"code": "85", "name": "Act of a person incapable of judgment by reason of intoxication caused against his will", "description": "Nothing is an offence which is done by a person who is intoxicated against his will"},
        {"code": "86", "name": "Offence requiring a particular intent or knowledge committed by one who is intoxicated", "description": "In cases where an act done is not an offence unless done with a particular knowledge or intent"},
        {"code": "87", "name": "Act not intended and not known to be likely to cause death or grievous hurt", "description": "Nothing which is not intended to cause death, or grievous hurt, and which is not known by the doer to be likely to cause death or grievous hurt"},
        {"code": "88", "name": "Act not intended to cause death, done by consent", "description": "Nothing, which is not intended to cause death, is an offence by reason of any harm which it may cause"},
        {"code": "89", "name": "Act done in good faith for benefit of child or insane person", "description": "Nothing which is done in good faith for the benefit of a person under twelve years of age, or of unsound mind"},
        {"code": "90", "name": "Consent known to be given under fear or misconception", "description": "A consent is not such a consent as is intended by any section of this Code, if the consent is given by a person under fear of injury"},
        {"code": "91", "name": "Exclusion of acts which are offences independently of harm caused", "description": "The exceptions in sections 87, 88 and 89 do not extend to acts which are offences independently of any harm which they may cause"},
        {"code": "92", "name": "Act done in good faith for benefit of a person without consent", "description": "Nothing is an offence by reason of any harm which it may cause to a person for whose benefit it is done in good faith"},
        {"code": "93", "name": "Communication made in good faith", "description": "No communication made in good faith is an offence by reason of any harm to the person to whom it is made"},
        {"code": "94", "name": "Act to which a person is compelled by threats", "description": "Except murder, and offences against the State punishable with death, nothing is an offence which is done by a person who is compelled to do it by threats"},
        {"code": "95", "name": "Act causing slight harm", "description": "Nothing is an offence by reason that it causes, or that it is intended to cause, or that it is known to be likely to cause, any harm"},
        {"code": "96", "name": "Things done in private defence", "description": "Nothing is an offence which is done in the exercise of the right of private defence"},
        {"code": "97", "name": "Right of private defence of the body and of property", "description": "Every person has a right to defend his own body, and the body of any other person, against any offence affecting the human body"},
        {"code": "98", "name": "Right of private defence against the act of a person of unsound mind", "description": "When an act, which would otherwise be a certain offence, is not that offence, by reason of the youth, the want of maturity of understanding"},
        {"code": "99", "name": "Acts against which there is no right of private defence", "description": "There is no right of private defence against an act which does not reasonably cause the apprehension of death or of grievous hurt"},
        {"code": "100", "name": "When the right of private defence of the body extends to causing death", "description": "The right of private defence of the body extends to the voluntary causing of death only when the assault causes reasonable apprehension of death"},
        {"code": "101", "name": "When such right extends to causing any harm other than death", "description": "If the offence be not of any of the descriptions enumerated in the last section, the right of private defence of the body does not extend to the voluntary causing of death"},
        {"code": "102", "name": "Commencement and continuance of the right of private defence of the body", "description": "The right of private defence of the body commences as soon as a reasonable apprehension of danger to the body arises from an attempt or threat to commit the offence"},
        {"code": "103", "name": "When the right of private defence of property extends to causing death", "description": "The right of private defence of property extends to the voluntary causing of death only when the offence is of certain descriptions"},
        {"code": "104", "name": "When such right extends to causing any harm other than death", "description": "If the offence, the committing of which, or the attempting to commit which occasions the exercise of the right of private defence"},
        {"code": "105", "name": "Commencement and continuance of the right of private defence of property", "description": "The right of private defence of property commences when a reasonable apprehension of danger to the property commences"},
        {"code": "106", "name": "Right of private defence against deadly assault when there is risk of harm to innocent person", "description": "If in the exercise of the right of private defence against an assault which reasonably causes the apprehension of death"},

        # Abetment (107-120)
        {"code": "107", "name": "Abetment of a thing", "description": "A person abets the doing of a thing, who instigates any person to do that thing, or engages with one or more other person or persons in any conspiracy"},
        {"code": "108", "name": "Abettor", "description": "A person abets an offence, who abets either the commission of an offence, or the commission of an act which would be an offence"},
        {"code": "109", "name": "Punishment of abetment if the act abetted is committed", "description": "Whoever abets any offence shall, if the act abetted is committed in consequence of the abetment"},
        {"code": "110", "name": "Punishment of abetment if person abetted does act with different intention", "description": "Whoever abets the commission of an offence shall, if the person abetted does the act with a different intention or knowledge"},
        {"code": "111", "name": "Liability of abettor when one act abetted and different act done", "description": "When an act is abetted and a different act is done, the abettor is liable for the act done, in the same manner and to the same extent"},
        {"code": "112", "name": "Abettor when liable to cumulative punishment", "description": "If the act for which the abettor is liable is committed in addition to the act abetted, and constitutes a distinct offence"},
        {"code": "113", "name": "Liability of abettor for an effect caused by the act abetted", "description": "When an act is abetted with the intention on the part of the abettor of causing a particular effect, and an act for which the abettor is liable"},
        {"code": "114", "name": "Abettor present when offence is committed", "description": "Whenever any person, who is absent would be liable to be punished as an abettor, is present when the act or offence for which he would be punishable"},
        {"code": "115", "name": "Abetment of offence punishable with death or imprisonment for life", "description": "Whoever abets the commission of an offence punishable with death or imprisonment for life"},
        {"code": "116", "name": "Abetment of offence punishable with imprisonment", "description": "Whoever abets an offence punishable with imprisonment shall, if that offence be not committed in consequence of the abetment"},
        {"code": "117", "name": "Abetting commission of offence by the public", "description": "Whoever abets the commission of an offence by the public generally or by any number or class of persons exceeding ten"},
        {"code": "118", "name": "Concealing design to commit offence punishable with death or imprisonment for life", "description": "Whoever intending to facilitate or knowing it to be likely that he will thereby facilitate the commission of an offence punishable with death or imprisonment for life"},
        {"code": "119", "name": "Public servant concealing design to commit offence", "description": "Whoever, being a public servant, intending to facilitate or knowing it to be likely that he will thereby facilitate the commission of an offence"},
        {"code": "120", "name": "Concealing design to commit offence punishable with imprisonment", "description": "Whoever, intending to facilitate or knowing it to be likely that he will thereby facilitate the commission of an offence punishable with imprisonment"},

        # Criminal Conspiracy (120A-120B)
        {"code": "120A", "name": "Definition of criminal conspiracy", "description": "When two or more persons agree to do, or cause to be done an illegal act, or an act which is not illegal by illegal means"},
        {"code": "120B", "name": "Punishment of criminal conspiracy", "description": "Whoever is a party to a criminal conspiracy to commit an offence punishable with death, imprisonment for life or rigorous imprisonment"},

        # Offenses Against the State (121-130)
        {"code": "121", "name": "Waging, or attempting to wage war, or abetting waging of war, against the Government of India", "description": "Whoever wages war against the Government of India, or attempts to wage such war, or abets the waging of such war"},
        {"code": "121A", "name": "Conspiracy to commit offences punishable by section 121", "description": "Whoever within or without India conspires to commit any of the offences punishable by section 121"},
        {"code": "122", "name": "Collecting arms, etc., with intention of waging war against the Government of India", "description": "Whoever collects men, arms or ammunition or otherwise prepares to wage war with the intention of either waging or being prepared to wage war against the Government of India"},
        {"code": "123", "name": "Concealing with intent to facilitate design to wage war", "description": "Whoever by any act, or by any illegal omission, conceals the existence of a design to wage war against the Government of India"},
        {"code": "124", "name": "Assaulting President, Governor, etc., with intent to compel or restrain the exercise of any lawful power", "description": "Whoever, with the intention of inducing or compelling the President of India, or Governor of any State"},
        {"code": "124A", "name": "Sedition", "description": "Whoever by words, either spoken or written, or by signs, or by visible representation, or otherwise, brings or attempts to bring into hatred or contempt"},
        {"code": "125", "name": "Waging war against any Asiatic Power in alliance with the Government of India", "description": "Whoever wages war against the Government of any Asiatic Power in alliance or at peace with the Government of India"},
        {"code": "126", "name": "Committing depredation on territories of Power at peace with the Government of India", "description": "Whoever commits depredation, or makes preparations to commit depredation, on the territories of any Power in alliance or at peace with the Government of India"},
        {"code": "127", "name": "Receiving property taken by war or depredation", "description": "Whoever receives any property knowing the same to have been taken in the commission of any of the offences mentioned in sections 125 and 126"},
        {"code": "128", "name": "Public servant voluntarily allowing prisoner of state or war to escape", "description": "Whoever, being a public servant and having the custody of any State prisoner or prisoner of war, voluntarily allows such prisoner to escape from any place"},
        {"code": "129", "name": "Public servant negligently suffering such prisoner to escape", "description": "Whoever, being a public servant and having the custody of any State prisoner or prisoner of war, negligently suffers such prisoner to escape from any place"},
        {"code": "130", "name": "Aiding escape of, rescuing or harbouring such prisoner", "description": "Whoever knowingly aids or assists any State prisoner or prisoner of war in escaping from lawful custody, or rescues or attempts to rescue any such prisoner"},

        # Offenses Against Public Tranquility (141-160)
        {"code": "141", "name": "Unlawful assembly", "description": "An assembly of five or more persons is designated an 'unlawful assembly', if the common object of the persons composing that assembly is to commit certain offenses"},
        {"code": "142", "name": "Being member of unlawful assembly", "description": "Whoever, being aware of facts which render any assembly an unlawful assembly, intentionally joins that assembly, or continues in it"},
        {"code": "143", "name": "Punishment for unlawful assembly", "description": "Whoever is a member of an unlawful assembly, shall be punished with imprisonment of either description for a term which may extend to six months"},
        {"code": "144", "name": "Joining unlawful assembly armed with deadly weapon", "description": "Whoever, being armed with any deadly weapon, or with anything which, used as a weapon of offence, is likely to cause death"},
        {"code": "145", "name": "Joining or continuing in unlawful assembly, knowing it has been commanded to disperse", "description": "Whoever joins or continues in an unlawful assembly, knowing that such unlawful assembly has been commanded to disperse"},
        {"code": "146", "name": "Rioting", "description": "Whenever force or violence is used by an unlawful assembly, or by any member thereof, in prosecution of the common object of such assembly"},
        {"code": "147", "name": "Punishment for rioting", "description": "Whoever is guilty of rioting, shall be punished with imprisonment of either description for a term which may extend to two years"},
        {"code": "148", "name": "Rioting, armed with deadly weapon", "description": "Whoever is guilty of rioting, being armed with a deadly weapon or with anything which, used as a weapon of offence, is likely to cause death"},
        {"code": "149", "name": "Every member of unlawful assembly guilty of offence committed in prosecution of common object", "description": "If an offence is committed by any member of an unlawful assembly in prosecution of the common object of that assembly"},
        {"code": "150", "name": "Hiring, or conniving at hiring, of persons to join unlawful assembly", "description": "Whoever hires or engages, or employs, or promotes, or connives at the hiring, engagement or employment of any person to join or become a member of any unlawful assembly"},
        {"code": "151", "name": "Knowingly joining or continuing in assembly of five or more persons after it has been commanded to disperse", "description": "Whoever knowingly joins or continues in any assembly of five or more persons likely to cause a disturbance of the public peace"},
        {"code": "152", "name": "Assaulting or obstructing public servant when suppressing riot, etc.", "description": "Whoever assaults or threatens to assault, or obstructs or attempts to obstruct, any public servant in the discharge of his duty"},
        {"code": "153", "name": "Wantonly giving provocation with intent to cause riot", "description": "Whoever malignantly, or wantonly by doing anything which is illegal, gives provocation to any person intending or knowing it to be likely that such provocation will cause the offence of rioting"},
        {"code": "153A", "name": "Promoting enmity between different groups", "description": "Whoever by words, either spoken or written, or by signs or by visible representations or otherwise, promotes or attempts to promote, on grounds of religion, race, place of birth, residence, language, caste or community or any other ground whatsoever, disharmony or feelings of enmity, hatred or ill-will between different religious, racial, language or regional groups or castes or communities"},
        {"code": "153B", "name": "Imputations, assertions prejudicial to national-integration", "description": "Whoever, by words either spoken or written or by signs or by visible representations or otherwise makes or publishes any imputation that any class of persons cannot, by reason of their being members of any religious, racial, language or regional group or caste or community, bear true faith and allegiance to the Constitution of India"},
        {"code": "154", "name": "Owner or occupier of land on which an unlawful assembly is held", "description": "Whenever any unlawful assembly or riot takes place, the owner or occupier of the land upon which such unlawful assembly is held, or such riot is committed"},
        {"code": "155", "name": "Liability of person for whose benefit riot is committed", "description": "Whenever a riot is committed for the benefit or on behalf of any person who is the owner or occupier of any land respecting which such riot takes place"},
        {"code": "156", "name": "Liability of agent of owner or occupier for whose benefit riot is committed", "description": "Where a riot is committed for the benefit or on behalf of any person who is the owner or occupier of any land respecting which such riot takes place"},
        {"code": "157", "name": "Harbouring persons hired for an unlawful assembly", "description": "Whoever harbours, receives or assembles, in any house or premises in his occupation or charge, or under his control any persons knowing that such persons have been hired, engaged or employed"},
        {"code": "158", "name": "Being hired to take part in an unlawful assembly or riot", "description": "Whoever is engaged, or hired, or offers or attempts to be hired or engaged, to do or assist in doing any of the acts specified in section 141"},
        {"code": "159", "name": "Affray", "description": "When two or more persons, by fighting in a public place, disturb the public peace, they are said to 'commit an affray'"},
        {"code": "160", "name": "Punishment for committing affray", "description": "Whoever commits an affray, shall be punished with imprisonment of either description for a term which may extend to one month"},

        # Offenses Against Public Servants (161-171)
        {"code": "166", "name": "Public servant disobeying law, with intent to cause injury to any person", "description": "Whoever, being a public servant, knowingly disobeys any direction of the law as to the way in which he is to conduct himself as such public servant"},
        {"code": "166A", "name": "Public servant disobeying direction under law", "description": "Whoever, being a public servant fails to record any information given to him under sub-section (1) of section 154 of the Code of Criminal Procedure, 1973"},
        {"code": "166B", "name": "Punishment for non-treatment of victim", "description": "Whoever, being in charge of a hospital, public or private, whether run by the Central Government, the State Government, local bodies or any other person"},
        {"code": "167", "name": "Public servant framing an incorrect document with intent to cause injury", "description": "Whoever, being a public servant, and being, as such public servant, charged with the preparation or translation of any document or electronic record"},
        {"code": "168", "name": "Public servant unlawfully engaging in trade", "description": "Whoever, being a public servant, and being legally bound as such public servant not to engage in trade, engages in trade"},
        {"code": "169", "name": "Public servant unlawfully buying or bidding for property", "description": "Whoever, being a public servant, and being legally bound as such public servant, not to purchase or bid for certain property, purchases or bids for that property"},
        {"code": "170", "name": "Personating a public servant", "description": "Whoever pretends to hold any particular office as a public servant, knowing that he does not hold such office or falsely personates any other person holding such office"},
        {"code": "171", "name": "Wearing garb or carrying token used by public servant with fraudulent intent", "description": "Whoever, not belonging to a certain class of public servants, wears any garb or carries any token resembling any garb or token used by that class of public servants"},

        # Offenses Against the Human Body
        {"code": "299", "name": "Culpable Homicide", "description": "Whoever causes death by doing an act with the intention of causing death"},
        {"code": "300", "name": "Murder", "description": "Culpable homicide is murder if done with the intention of causing death"},
        {"code": "302", "name": "Punishment for Murder", "description": "Whoever commits murder shall be punished with death or imprisonment for life"},
        {"code": "304", "name": "Culpable Homicide not amounting to Murder", "description": "Punishment for culpable homicide not amounting to murder"},
        {"code": "304A", "name": "Death by Negligence", "description": "Causing death by negligence"},
        {"code": "304B", "name": "Dowry Death", "description": "Death of a woman caused by burns or bodily injury within 7 years of marriage"},
        {"code": "305", "name": "Abetment of Suicide", "description": "Abetment of suicide of child or insane person"},
        {"code": "306", "name": "Abetment of Suicide", "description": "If any person commits suicide, whoever abets the commission of such suicide"},
        {"code": "307", "name": "Attempt to Murder", "description": "Attempt to murder by doing an act with the intention of causing death"},
        {"code": "308", "name": "Attempt to Culpable Homicide", "description": "Attempt to commit culpable homicide not amounting to murder"},
        {"code": "309", "name": "Attempt to Suicide", "description": "Attempt to commit suicide and doing any act towards the commission of such offence"},
        {"code": "312", "name": "Causing Miscarriage", "description": "Voluntarily causing a woman with child to miscarry"},
        {"code": "319", "name": "Hurt", "description": "Whoever causes bodily pain, disease or infirmity to any person"},
        {"code": "320", "name": "Grievous Hurt", "description": "Emasculation, permanent privation of sight or hearing, etc."},
        {"code": "321", "name": "Voluntarily Causing Hurt", "description": "Voluntarily causing hurt"},
        {"code": "322", "name": "Voluntarily Causing Grievous Hurt", "description": "Voluntarily causing grievous hurt"},
        {"code": "323", "name": "Punishment for Hurt", "description": "Punishment for voluntarily causing hurt"},
        {"code": "324", "name": "Hurt by Dangerous Weapons", "description": "Voluntarily causing hurt by dangerous weapons or means"},
        {"code": "325", "name": "Punishment for Grievous Hurt", "description": "Punishment for voluntarily causing grievous hurt"},
        {"code": "326", "name": "Grievous Hurt by Dangerous Weapons", "description": "Voluntarily causing grievous hurt by dangerous weapons or means"},
        {"code": "326A", "name": "Acid Attack", "description": "Voluntarily causing grievous hurt by use of acid"},
        {"code": "326B", "name": "Attempt to Acid Attack", "description": "Voluntarily throwing or attempting to throw acid"},
        {"code": "327", "name": "Voluntarily causing hurt to extort property", "description": "Voluntarily causing hurt to extort property or to constrain to an illegal act"},
        {"code": "328", "name": "Causing hurt by poison", "description": "Causing hurt by means of poison with intent to commit an offence"},
        {"code": "329", "name": "Voluntarily causing grievous hurt to extort property", "description": "Voluntarily causing grievous hurt to extort property or to constrain to an illegal act"},
        {"code": "334", "name": "Voluntarily causing hurt on provocation", "description": "Voluntarily causing hurt on grave and sudden provocation"},
        {"code": "335", "name": "Voluntarily causing grievous hurt on provocation", "description": "Voluntarily causing grievous hurt on grave and sudden provocation"},
        {"code": "336", "name": "Act endangering life or personal safety", "description": "Doing any act which endangers human life or personal safety of others"},
        {"code": "337", "name": "Causing hurt by act endangering life", "description": "Causing hurt by act endangering life or personal safety of others"},
        {"code": "338", "name": "Causing grievous hurt by act endangering life", "description": "Causing grievous hurt by act endangering life or personal safety of others"},
        {"code": "339", "name": "Wrongful restraint", "description": "Voluntarily obstructing any person so as to prevent that person from proceeding in any direction"},
        {"code": "340", "name": "Wrongful confinement", "description": "Wrongfully restraining any person in such a manner as to prevent that person from proceeding beyond certain circumscribing limits"},
        {"code": "341", "name": "Punishment for wrongful restraint", "description": "Punishment for wrongful restraint"},
        {"code": "342", "name": "Punishment for wrongful confinement", "description": "Punishment for wrongful confinement"},
        {"code": "343", "name": "Wrongful confinement for three or more days", "description": "Wrongful confinement for three days or more"},
        {"code": "344", "name": "Wrongful confinement for ten or more days", "description": "Wrongful confinement for ten days or more"},
        {"code": "346", "name": "Wrongful confinement in secret", "description": "Wrongful confinement in secret"},
        {"code": "350", "name": "Criminal force", "description": "Using force to any person without that person's consent, in order to commit an offence"},
        {"code": "351", "name": "Assault", "description": "Making a gesture or preparation, intending or knowing it to be likely that such gesture or preparation will cause any person present to apprehend that criminal force will be used"},
        {"code": "352", "name": "Punishment for assault or criminal force", "description": "Punishment for assault or criminal force otherwise than on grave provocation"},
        {"code": "354", "name": "Assault on Woman", "description": "Assault or criminal force to woman with intent to outrage her modesty"},
        {"code": "354A", "name": "Sexual harassment", "description": "Sexual harassment and punishment for sexual harassment"},
        {"code": "354B", "name": "Assault with intent to disrobe", "description": "Assault or use of criminal force to woman with intent to disrobe"},
        {"code": "354C", "name": "Voyeurism", "description": "Watching or capturing the image of a woman engaging in a private act"},
        {"code": "354D", "name": "Stalking", "description": "Following a woman and contacting, or attempting to contact such woman to foster personal interaction repeatedly despite a clear indication of disinterest"},
        {"code": "359", "name": "Kidnapping", "description": "Kidnapping is of two kinds: kidnapping from India, and kidnapping from lawful guardianship"},
        {"code": "363", "name": "Punishment for kidnapping", "description": "Punishment for kidnapping"},
        {"code": "363A", "name": "Kidnapping or maiming a minor for begging", "description": "Kidnapping or maiming a minor for purposes of begging"},
        {"code": "366", "name": "Kidnapping or abducting a woman", "description": "Kidnapping, abducting or inducing woman to compel her marriage, etc."},
        {"code": "366A", "name": "Procuration of minor girl", "description": "Procuration of minor girl under eighteen years of age"},
        {"code": "366B", "name": "Importation of girl from foreign country", "description": "Importation of girl from foreign country under twenty-one years of age"},
        {"code": "370", "name": "Trafficking of person", "description": "Trafficking of person for exploitation"},
        {"code": "370A", "name": "Exploitation of a trafficked person", "description": "Exploitation of a trafficked child or person"},
        {"code": "375", "name": "Rape", "description": "Sexual intercourse with a woman against her will, without her consent, etc."},
        {"code": "376", "name": "Punishment for rape", "description": "Punishment for committing rape"},
        {"code": "376A", "name": "Causing death resulting in persistent vegetative state", "description": "Punishment for causing death or resulting in persistent vegetative state of victim during rape"},
        {"code": "376B", "name": "Sexual intercourse by husband upon his wife during separation", "description": "Sexual intercourse by husband upon his wife during separation"},
        {"code": "376C", "name": "Sexual intercourse by a person in authority", "description": "Sexual intercourse by a person in authority or in a fiduciary relationship"},
        {"code": "376D", "name": "Gang rape", "description": "Where a woman is raped by one or more persons constituting a group"},
        {"code": "376E", "name": "Repeat offenders", "description": "Punishment for repeat offenders of rape"},

        # Offenses Against Property
        {"code": "378", "name": "Theft", "description": "Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent"},
        {"code": "379", "name": "Punishment for theft", "description": "Punishment for theft"},
        {"code": "380", "name": "Theft in dwelling house", "description": "Theft in dwelling house, etc."},
        {"code": "381", "name": "Theft by clerk or servant", "description": "Theft by clerk or servant of property in possession of master"},
        {"code": "382", "name": "Theft after preparation to cause death or hurt", "description": "Theft after preparation made for causing death, hurt or restraint in order to commit theft"},
        {"code": "383", "name": "Extortion", "description": "Putting any person in fear of injury to commit extortion"},
        {"code": "384", "name": "Punishment for extortion", "description": "Punishment for extortion"},
        {"code": "385", "name": "Putting person in fear of injury", "description": "Putting person in fear of injury in order to commit extortion"},
        {"code": "386", "name": "Extortion by putting a person in fear of death", "description": "Extortion by putting a person in fear of death or grievous hurt"},
        {"code": "387", "name": "Putting person in fear of death", "description": "Putting person in fear of death or of grievous hurt, in order to commit extortion"},
        {"code": "388", "name": "Extortion by threat of accusation", "description": "Extortion by threat of accusation of an offence punishable with death or imprisonment for life, etc."},
        {"code": "389", "name": "Putting person in fear of accusation", "description": "Putting person in fear of accusation of offence punishable with death or imprisonment for life"},
        {"code": "390", "name": "Robbery", "description": "In all robbery there is either theft or extortion"},
        {"code": "391", "name": "Dacoity", "description": "When five or more persons conjointly commit or attempt to commit a robbery"},
        {"code": "392", "name": "Punishment for robbery", "description": "Punishment for robbery"},
        {"code": "393", "name": "Attempt to commit robbery", "description": "Attempt to commit robbery"},
        {"code": "394", "name": "Voluntarily causing hurt in committing robbery", "description": "Voluntarily causing hurt in committing robbery"},
        {"code": "395", "name": "Punishment for dacoity", "description": "Punishment for dacoity"},
        {"code": "396", "name": "Dacoity with murder", "description": "Dacoity with murder"},
        {"code": "397", "name": "Robbery or dacoity with attempt to cause death", "description": "Robbery, or dacoity, with attempt to cause death or grievous hurt"},
        {"code": "398", "name": "Attempt to commit robbery or dacoity when armed", "description": "Attempt to commit robbery or dacoity when armed with deadly weapon"},
        {"code": "399", "name": "Making preparation to commit dacoity", "description": "Making preparation to commit dacoity"},
        {"code": "402", "name": "Assembling for purpose of committing dacoity", "description": "Assembling for purpose of committing dacoity"},
        {"code": "403", "name": "Dishonest misappropriation of property", "description": "Dishonest misappropriation of property"},
        {"code": "404", "name": "Dishonest misappropriation of property of deceased person", "description": "Dishonest misappropriation of property possessed by deceased person at the time of his death"},
        {"code": "405", "name": "Criminal breach of trust", "description": "Criminal breach of trust"},
        {"code": "406", "name": "Punishment for criminal breach of trust", "description": "Punishment for criminal breach of trust"},
        {"code": "407", "name": "Criminal breach of trust by carrier", "description": "Criminal breach of trust by carrier, etc."},
        {"code": "408", "name": "Criminal breach of trust by clerk or servant", "description": "Criminal breach of trust by clerk or servant"},
        {"code": "409", "name": "Criminal breach of trust by public servant", "description": "Criminal breach of trust by public servant, or by banker, merchant or agent"},
        {"code": "410", "name": "Stolen property", "description": "Stolen property"},
        {"code": "411", "name": "Dishonestly receiving stolen property", "description": "Dishonestly receiving stolen property"},
        {"code": "412", "name": "Dishonestly receiving property stolen in dacoity", "description": "Dishonestly receiving property stolen in the commission of a dacoity"},
        {"code": "413", "name": "Habitually dealing in stolen property", "description": "Habitually dealing in stolen property"},
        {"code": "414", "name": "Assisting in concealment of stolen property", "description": "Assisting in concealment of stolen property"},
        {"code": "415", "name": "Cheating", "description": "Whoever, by deceiving any person, fraudulently or dishonestly induces the person so deceived to deliver any property to any person"},
        {"code": "416", "name": "Cheating by personation", "description": "A person is said to 'cheat by personation' if he cheats by pretending to be some other person"},
        {"code": "417", "name": "Punishment for cheating", "description": "Punishment for cheating"},
        {"code": "418", "name": "Cheating with knowledge that wrongful loss may ensue", "description": "Cheating with knowledge that wrongful loss may ensue to person whose interest offender is bound to protect"},
        {"code": "419", "name": "Punishment for cheating by personation", "description": "Punishment for cheating by personation"},
        {"code": "420", "name": "Cheating and dishonestly inducing delivery of property", "description": "Cheating and dishonestly inducing delivery of property"},
        {"code": "421", "name": "Dishonest or fraudulent removal or concealment of property", "description": "Dishonest or fraudulent removal or concealment of property to prevent distribution among creditors"},
        {"code": "422", "name": "Dishonestly or fraudulently preventing debt being available", "description": "Dishonestly or fraudulently preventing debt being available for creditors"},
        {"code": "423", "name": "Dishonest or fraudulent execution of deed of transfer", "description": "Dishonest or fraudulent execution of deed of transfer containing false statement of consideration"},
        {"code": "424", "name": "Dishonest or fraudulent removal or concealment of property", "description": "Dishonest or fraudulent removal or concealment of property"},
        {"code": "425", "name": "Mischief", "description": "Whoever with intent to cause, or knowing that he is likely to cause, wrongful loss or damage to the public or to any person"},
        {"code": "426", "name": "Punishment for mischief", "description": "Punishment for mischief"},
        {"code": "427", "name": "Mischief causing damage", "description": "Mischief causing damage to the amount of fifty rupees"},
        {"code": "428", "name": "Mischief by killing or maiming animal", "description": "Mischief by killing or maiming animal of the value of ten rupees"},
        {"code": "429", "name": "Mischief by killing or maiming cattle", "description": "Mischief by killing or maiming cattle, etc., of any value or any animal of the value of fifty rupees"},
        {"code": "430", "name": "Mischief by injury to works of irrigation", "description": "Mischief by injury to works of irrigation or by wrongfully diverting water"},
        {"code": "431", "name": "Mischief by injury to public road", "description": "Mischief by injury to public road, bridge, river or channel"},
        {"code": "434", "name": "Mischief by destroying or moving landmark", "description": "Mischief by destroying or moving, etc., a landmark fixed by public authority"},
        {"code": "435", "name": "Mischief by fire or explosive substance", "description": "Mischief by fire or explosive substance with intent to cause damage"},
        {"code": "436", "name": "Mischief by fire or explosive substance with intent to destroy house", "description": "Mischief by fire or explosive substance with intent to destroy house, etc."},
        {"code": "437", "name": "Mischief with intent to destroy vessel", "description": "Mischief with intent to destroy or make unsafe a decked vessel or one of twenty tons burden"},
        {"code": "438", "name": "Mischief by fire or explosive substance with intent to destroy vessel", "description": "Punishment for the mischief described in section 437 committed by fire or explosive substance"},
        {"code": "439", "name": "Punishment for intentionally running vessel aground", "description": "Punishment for intentionally running vessel aground or ashore with intent to commit theft, etc."},
        {"code": "440", "name": "Mischief committed after preparation made for causing death", "description": "Mischief committed after preparation made for causing death or hurt"},
        {"code": "447", "name": "Punishment for criminal trespass", "description": "Punishment for criminal trespass"},
        {"code": "448", "name": "Punishment for house-trespass", "description": "Punishment for house-trespass"},
        {"code": "449", "name": "House-trespass in order to commit offence punishable with death", "description": "House-trespass in order to commit offence punishable with death"},
        {"code": "450", "name": "House-trespass in order to commit offence punishable with imprisonment for life", "description": "House-trespass in order to commit offence punishable with imprisonment for life"},
        {"code": "451", "name": "House-trespass in order to commit offence", "description": "House-trespass in order to commit offence punishable with imprisonment"},
        {"code": "452", "name": "House-trespass after preparation for hurt, assault or wrongful restraint", "description": "House-trespass after preparation for hurt, assault or wrongful restraint"},
        {"code": "453", "name": "Punishment for lurking house-trespass or house-breaking", "description": "Punishment for lurking house-trespass or house-breaking"},
        {"code": "454", "name": "Lurking house-trespass or house-breaking in order to commit offence", "description": "Lurking house-trespass or house-breaking in order to commit offence punishable with imprisonment"},
        {"code": "455", "name": "Lurking house-trespass or house-breaking after preparation for hurt", "description": "Lurking house-trespass or house-breaking after preparation for hurt, assault or wrongful restraint"},
        {"code": "456", "name": "Punishment for lurking house-trespass or house-breaking by night", "description": "Punishment for lurking house-trespass or house-breaking by night"},
        {"code": "457", "name": "Lurking house-trespass or house-breaking by night in order to commit offence", "description": "Lurking house-trespass or house-breaking by night in order to commit offence punishable with imprisonment"},
        {"code": "458", "name": "Lurking house-trespass or house-breaking by night after preparation for hurt", "description": "Lurking house-trespass or house-breaking by night after preparation for hurt, assault, or wrongful restraint"},
        {"code": "459", "name": "Grievous hurt caused whilst committing lurking house-trespass or house-breaking", "description": "Grievous hurt caused whilst committing lurking house-trespass or house-breaking"},
        {"code": "460", "name": "Death or grievous hurt caused by one of several persons", "description": "All persons jointly concerned in lurking house-trespass or house-breaking by night punishable where death or grievous hurt caused by one of them"},

        # Offenses Against Public Tranquility
        {"code": "498A", "name": "Cruelty by Husband or Relatives", "description": "Husband or relative of husband of a woman subjecting her to cruelty"},
        {"code": "499", "name": "Defamation", "description": "Whoever, by words either spoken or intended to be read, or by signs or by visible representations, makes or publishes any imputation concerning any person"},
        {"code": "500", "name": "Punishment for defamation", "description": "Punishment for defamation"},
        {"code": "503", "name": "Criminal intimidation", "description": "Whoever threatens another with any injury to his person, reputation or property"},
        {"code": "504", "name": "Intentional insult with intent to provoke breach of the peace", "description": "Intentional insult with intent to provoke breach of the peace"},
        {"code": "505", "name": "Statements conducing to public mischief", "description": "Statements conducing to public mischief"},
        {"code": "506", "name": "Punishment for criminal intimidation", "description": "Punishment for criminal intimidation"},
        {"code": "507", "name": "Criminal intimidation by an anonymous communication", "description": "Criminal intimidation by an anonymous communication"},
        {"code": "508", "name": "Act caused by inducing person to believe that he will be rendered an object of the Divine displeasure", "description": "Act caused by inducing person to believe that he will be rendered an object of the Divine displeasure"},
        {"code": "509", "name": "Word, gesture or act intended to insult the modesty of a woman", "description": "Word, gesture or act intended to insult the modesty of a woman"},
        {"code": "510", "name": "Misconduct in public by a drunken person", "description": "Misconduct in public by a drunken person"}
    ]

    # Add sections to database
    for section_data in sections:
        section = LegalSection(
            code=section_data["code"],
            name=section_data["name"],
            description=section_data["description"]
        )
        db.session.add(section)

    db.session.commit()

def get_legal_sections_for_fir(legal_mapping_data):
    """
    Get the LegalSection objects based on the legal mapping data from the AI

    Args:
        legal_mapping_data: The JSON data returned by the AI containing section mappings

    Returns:
        list: List of dictionaries containing LegalSection objects and metadata
    """
    result_sections = []

    try:
        # Extract section data from the mapping data
        mapped_sections = legal_mapping_data.get('sections', [])
        section_codes = [section.get('section_code') for section in mapped_sections if 'section_code' in section]

        # Query the database for these sections
        if section_codes:
            # Filter out any 'N/A' codes (used for error messages)
            valid_codes = [code for code in section_codes if code != 'N/A']

            if valid_codes:
                db_sections = LegalSection.query.filter(LegalSection.code.in_(valid_codes)).all()

                # Create a mapping of code to section object
                db_section_map = {section.code: section for section in db_sections}

                # Process each mapped section
                for section_data in mapped_sections:
                    code = section_data.get('section_code')

                    # Skip 'N/A' sections
                    if code == 'N/A':
                        result_sections.append({
                            'code': 'N/A',
                            'name': section_data.get('section_name', 'Unknown Section'),
                            'description': section_data.get('section_description', ''),
                            'relevance': section_data.get('relevance', ''),
                            'confidence': section_data.get('confidence', 0)
                        })
                        continue

                    # Get or create the section
                    if code in db_section_map:
                        section = db_section_map[code]
                    else:
                        # Create new section if it doesn't exist
                        section = LegalSection(
                            code=code,
                            name=section_data.get('section_name', f"Section {code}"),
                            description=section_data.get('section_description', "")
                        )
                        db.session.add(section)
                        db_section_map[code] = section

                    # Add section with metadata to results
                    result_sections.append({
                        'code': section.code,
                        'name': section.name,
                        'description': section.description,
                        'relevance': section_data.get('relevance', ''),
                        'confidence': section_data.get('confidence', 0.5)  # Default confidence if not provided
                    })

                # Commit any new sections to the database
                db.session.commit()

            # If we have error sections (N/A), add them
            elif 'N/A' in section_codes:
                for section_data in mapped_sections:
                    if section_data.get('section_code') == 'N/A':
                        result_sections.append({
                            'code': 'N/A',
                            'name': section_data.get('section_name', 'Unknown Section'),
                            'description': section_data.get('section_description', ''),
                            'relevance': section_data.get('relevance', ''),
                            'confidence': section_data.get('confidence', 0)
                        })
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error getting legal sections: {e}", exc_info=True)
        # Add an error section
        result_sections.append({
            'code': 'ERR',
            'name': 'Error Processing Sections',
            'description': 'An error occurred while processing the legal sections.',
            'relevance': str(e),
            'confidence': 0
        })

    # Sort sections by confidence (highest first)
    result_sections.sort(key=lambda x: x.get('confidence', 0), reverse=True)

    return result_sections
