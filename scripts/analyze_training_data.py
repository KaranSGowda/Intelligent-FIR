"""
Script to analyze the training data used in the ML model.
"""

from app import app
from utils.ml_analyzer import train_model

def analyze_training_data():
    """Analyze the training data used in the ML model."""
    # Access the default training data
    training_data = [
        # Section 302 - Murder
        ("The accused murdered the victim by stabbing him multiple times.", ["302"]),
        ("The victim was killed by the accused with a knife.", ["302"]),
        ("The accused shot and killed the victim during an argument.", ["302"]),
        ("The accused strangled the victim to death.", ["302"]),
        ("The victim died due to poisoning administered by the accused.", ["302"]),
        ("The accused hit the victim on the head with a heavy object causing death.", ["302"]),
        ("The accused deliberately ran over the victim with a car, killing them instantly.", ["302"]),

        # Section 307 - Attempt to Murder
        ("The accused attempted to kill the victim by firing a gun.", ["307"]),
        ("The accused tried to stab the victim but was stopped.", ["307"]),
        ("The accused poisoned the food but the victim survived after hospital treatment.", ["307"]),
        ("The accused pushed the victim from a height with intent to kill, but the victim survived.", ["307"]),
        ("The accused attacked the victim with a deadly weapon but failed to kill them.", ["307"]),
        ("The accused tried to strangle the victim but was interrupted.", ["307"]),

        # Section 323 - Voluntarily causing hurt
        ("The accused assaulted the victim causing injuries.", ["323"]),
        ("The accused slapped and punched the victim.", ["323"]),
        ("The accused beat the victim with bare hands.", ["323"]),
        ("The victim was physically assaulted by the accused.", ["323"]),
        ("The accused pushed the victim causing them to fall and get injured.", ["323"]),

        # Section 324 - Voluntarily causing hurt by dangerous weapons
        ("The accused attacked the victim with a knife causing injuries.", ["324"]),
        ("The accused hit the victim with an iron rod.", ["324"]),
        ("The accused used a broken bottle to attack the victim.", ["324"]),
        ("The victim was injured when the accused attacked with a sharp object.", ["324"]),
        ("The accused threw acid at the victim causing burns.", ["324"]),

        # Section 354 - Assault or criminal force to woman with intent to outrage her modesty
        ("The accused inappropriately touched a woman without her consent.", ["354"]),
        ("The accused groped the woman in a public place.", ["354"]),
        ("The accused forcibly hugged the woman against her will.", ["354"]),
        ("The woman was molested by the accused in the elevator.", ["354"]),
        ("The accused pulled the woman's clothes with intent to disrobe her.", ["354"]),

        # Section 376 - Rape
        ("The accused sexually assaulted the victim.", ["376"]),
        ("The accused raped the victim at his residence.", ["376"]),
        ("The victim was sexually violated by the accused against her consent.", ["376"]),
        ("The accused committed sexual intercourse with the victim without consent.", ["376"]),

        # Section 379 - Theft
        ("The accused stole the victim's mobile phone.", ["379"]),
        ("The accused took the victim's wallet from their pocket.", ["379"]),
        ("The victim's laptop was stolen by the accused from the office.", ["379"]),
        ("The accused stole jewelry from the victim's bag.", ["379"]),
        ("The accused took the victim's bicycle without permission.", ["379"]),

        # Section 380 - Theft in dwelling house
        ("The accused broke into the victim's house and stole valuables.", ["380"]),
        ("The accused entered the house at night and stole electronics.", ["380"]),
        ("The victim's home was burglarized by the accused who stole cash and jewelry.", ["380"]),
        ("The accused stole items from the victim's apartment while they were away.", ["380"]),

        # Section 384 - Extortion
        ("The accused threatened the victim and demanded money.", ["384", "506"]),
        ("The accused blackmailed the victim for financial gain.", ["384"]),
        ("The victim was forced to pay money after being threatened by the accused.", ["384", "506"]),
        ("The accused extorted money by threatening to harm the victim's family.", ["384", "506"]),

        # Section 392 - Robbery
        ("The accused robbed the victim at knifepoint.", ["392"]),
        ("The accused snatched the victim's purse using force.", ["392"]),
        ("The victim was robbed by the accused who threatened with a weapon.", ["392"]),
        ("The accused forcibly took the victim's belongings after assaulting them.", ["392", "323"]),

        # Section 395 - Dacoity
        ("A group of five armed men robbed the bank.", ["395"]),
        ("The shop was looted by a gang of seven people.", ["395"]),
        ("Five or more persons committed robbery at the victim's house.", ["395"]),
        ("A gang of armed dacoits attacked and robbed the village.", ["395"]),

        # Section 406 - Criminal breach of trust
        ("The accused misappropriated the funds entrusted to him.", ["406"]),
        ("The accused was given jewelry for safekeeping but sold it.", ["406"]),
        ("The victim gave money to the accused for investment but the accused used it for personal expenses.", ["406"]),
        ("The accused was entrusted with documents but destroyed them.", ["406"]),

        # Section 420 - Cheating and dishonestly inducing delivery of property
        ("The accused cheated the victim by selling fake property documents.", ["420"]),
        ("The accused fraudulently took money promising a job that didn't exist.", ["420"]),
        ("The victim was deceived into investing in a fake company by the accused.", ["420"]),
        ("The accused sold counterfeit products claiming them to be genuine.", ["420"]),
        ("The accused ran a Ponzi scheme defrauding multiple victims.", ["420"]),

        # Section 498A - Husband or relative of husband of a woman subjecting her to cruelty
        ("The husband and in-laws harassed the woman for dowry.", ["498A"]),
        ("The woman was subjected to cruelty by her husband.", ["498A"]),
        ("The victim's husband and mother-in-law tortured her for not bringing enough dowry.", ["498A"]),
        ("The woman was physically and mentally abused by her husband.", ["498A"]),

        # Section 504 - Intentional insult with intent to provoke breach of the peace
        ("The accused verbally abused the victim in public.", ["504"]),
        ("The accused used derogatory language to insult the victim.", ["504"]),
        ("The accused deliberately provoked the victim with insulting words.", ["504"]),
        ("The victim was publicly humiliated by the accused's insulting remarks.", ["504"]),

        # Section 506 - Criminal intimidation
        ("The accused threatened to kill the victim.", ["506"]),
        ("The accused threatened to harm the victim's children if demands weren't met.", ["506"]),
        ("The victim received death threats from the accused.", ["506"]),
        ("The accused intimidated the victim with threats of violence.", ["506"]),

        # Section 509 - Word, gesture or act intended to insult the modesty of a woman
        ("The accused made inappropriate gestures towards a woman.", ["509"]),
        ("The accused passed lewd comments at the woman.", ["509"]),
        ("The woman was harassed by the accused making obscene gestures.", ["509"]),
        ("The accused stalked the woman and made vulgar comments.", ["509"]),

        # Multiple sections
        ("The accused broke into the house, stole valuables, and assaulted the owner.", ["380", "323"]),
        ("The accused kidnapped the victim and demanded ransom from the family.", ["363", "384"]),
        ("The accused forged documents to fraudulently sell the victim's property.", ["420", "468"]),
        ("The accused threatened witnesses to prevent them from testifying in court.", ["506", "195"]),
        ("The accused was driving under the influence and caused a fatal accident.", ["304A", "279"]),
        ("The accused cyberstalked the victim and posted obscene content about them online.", ["509", "67A"]),
        ("The accused trespassed into the victim's property and damaged furniture.", ["447", "427"])
    ]
    
    # Extract all unique section codes from the training data
    all_sections = set()
    for _, sections in training_data:
        all_sections.update(sections)
    
    # Count examples for each section
    section_counts = {}
    for _, sections in training_data:
        for section in sections:
            if section in section_counts:
                section_counts[section] += 1
            else:
                section_counts[section] = 1
    
    # Print results
    print(f"Total unique IPC sections in training data: {len(all_sections)}")
    print("\nIPC sections in training data:")
    print(", ".join(sorted(list(all_sections))))
    
    print("\nNumber of examples per section:")
    for section, count in sorted(section_counts.items()):
        print(f"Section {section}: {count} examples")

if __name__ == "__main__":
    with app.app_context():
        analyze_training_data()
