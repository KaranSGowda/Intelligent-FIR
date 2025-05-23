"""
Machine Learning based complaint analyzer for IPC section classification.
This module uses NLP techniques to analyze complaint text and determine
relevant IPC sections that may apply.
"""

import re
import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import MultiLabelBinarizer
import pickle
import os
import logging
from extensions import db
from models import LegalSection

# Configure logging
logger = logging.getLogger(__name__)

# Download required NLTK resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK resources: {str(e)}")

# Create a simple lemmatizer class as a fallback
class SimpleLemmatizer:
    def lemmatize(self, word):
        """Simple lemmatizer that just returns the word unchanged"""
        return word

# Initialize lemmatizer and stopwords
try:
    # Try to download wordnet again if it's not properly loaded
    try:
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)  # Open Multilingual WordNet
    except Exception as download_error:
        logger.warning(f"Error downloading additional NLTK data: {str(download_error)}")

    # Try to use the NLTK lemmatizer
    lemmatizer = WordNetLemmatizer()
    # Test the lemmatizer with a simple word to ensure it works
    test_word = lemmatizer.lemmatize('test')
    logger.info(f"Lemmatizer initialized successfully, test: 'test' -> '{test_word}'")

    # Initialize stopwords
    stop_words = set(stopwords.words('english'))
except Exception as e:
    logger.warning(f"Error initializing NLP components: {str(e)}")
    # Fallback to our simple lemmatizer and empty stopwords
    lemmatizer = SimpleLemmatizer()
    stop_words = set()
    logger.info("Using fallback SimpleLemmatizer")

# Add domain-specific stopwords
legal_stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'}
stop_words.update(legal_stopwords)

# Model file paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml_models')
os.makedirs(MODEL_DIR, exist_ok=True)
VECTORIZER_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')
CLASSIFIER_PATH = os.path.join(MODEL_DIR, 'ipc_classifier.pkl')
BINARIZER_PATH = os.path.join(MODEL_DIR, 'multilabel_binarizer.pkl')

# IPC keywords mapping - these are keywords associated with specific IPC sections
IPC_KEYWORDS = {
    '1': ['and', 'title', 'of', 'title and extent of operation of the code', 'extent', 'the', 'operation', 'code'],
    '100': ['to', 'causing', 'extends', 'the assault causes', 'body', 'assault causes', 'of', 'death', 'the assault', 'assault', 'private', 'when', 'death only', 'of death only', 'of death', 'right', 'the', 'defence', 'when the right of private defence of the body extends to causing death'],
    '101': ['any', 'of death', 'to', 'other', 'when', 'such', 'causing', 'extends', 'right', 'harm', 'than', 'when such right extends to causing any harm other than death', 'death'],
    '102': ['body', 'and', 'or threat to', 'or threat', 'of', 'threat to', 'private', 'commencement and continuance of the right of private defence of the body', 'continuance', 'right', 'the', 'defence', 'threat', 'commencement'],
    '103': ['of death only', 'of death', 'of property extends', 'to', 'of', 'private', 'when', 'death only', 'causing', 'extends', 'right', 'the', 'of property', 'when the right of private defence of property extends to causing death', 'property extends', 'defence', 'property', 'death'],
    '104': ['any', 'to', 'other', 'when', 'such', 'causing', 'extends', 'right', 'harm', 'than', 'when such right extends to causing any harm other than death', 'death'],
    '105': ['and', 'commencement and continuance of the right of private defence of property', 'of', 'private', 'continuance', 'property commences', 'of property commences', 'right', 'the', 'property', 'of property', 'defence', 'commencement'],
    '106': ['to', 'person', 'an assault', 'there', 'harm', 'right of private defence against deadly assault when there is risk of harm to innocent person', 'assault which', 'innocent', 'of', 'deadly', 'death', 'is', 'assault', 'private', 'risk', 'when', 'of death', 'against', 'an assault which', 'right', 'defence'],
    '107': ['abetment', 'abetment of a thing', 'of', 'thing', 'a'],
    '108': ['abettor'],
    '109': ['abetment', 'if', 'of', 'is', 'act', 'punishment of abetment if the act abetted is committed', 'punishment', 'the', 'committed', 'abetted'],
    '110': ['abetment', 'if', 'of', 'intention', 'person', 'act', 'punishment', 'does', 'punishment of abetment if person abetted does act with different intention', 'with', 'abetted', 'different'],
    '111': ['and', 'one', 'abettor', 'of', 'liability', 'act', 'liability of abettor when one act abetted and different act done', 'when', 'done', 'abetted', 'different'],
    '112': ['to', 'abettor when liable to cumulative punishment', 'abettor', 'liable', 'punishment', 'when', 'cumulative'],
    '113': ['by', 'abetted', 'abettor', 'of', 'liability', 'act', 'liability of abettor for an effect caused by the act abetted', 'for', 'the', 'an', 'effect', 'caused'],
    '114': ['abettor', 'is', 'abettor present when offence is committed', 'when', 'offence', 'present', 'committed'],
    '115': ['imprisonment', 'abetment', 'with death or', 'of', 'offence', 'punishable', 'or', 'for', 'death or', 'life', 'with', 'with death', 'death', 'abetment of offence punishable with death or imprisonment for life'],
    '116': ['imprisonment', 'abetment', 'of', 'abetment of offence punishable with imprisonment', 'offence', 'punishable', 'with'],
    '117': ['by', 'of', 'commission', 'offence', 'abetting', 'abetting commission of offence by the public', 'the', 'public'],
    '118': ['death', 'imprisonment', 'life', 'to', 'with death or', 'offence', 'punishable', 'or', 'for', 'concealing design to commit offence punishable with death or imprisonment for life', 'commit', 'design', 'with', 'with death', 'concealing', 'death or'],
    '119': ['public servant concealing design to commit offence', 'to', 'a public servant', 'public servant', 'offence', 'commit', 'design', 'public', 'servant', 'concealing'],
    '120': ['imprisonment', 'to', 'concealing design to commit offence punishable with imprisonment', 'offence', 'punishable', 'commit', 'design', 'with', 'concealing'],
    '120A': ['conspiracy', 'illegal', 'an illegal', 'of', 'illegal act', 'criminal', 'an illegal act', 'definition', 'definition of criminal conspiracy'],
    '120B': ['conspiracy', 'with death', 'a criminal', 'of', 'punishment', 'criminal conspiracy', 'criminal', 'a criminal conspiracy', 'punishment of criminal conspiracy', 'death'],
    '121': ['the government', 'to', 'government of', 'government', 'of', 'against', 'attempting', 'india', 'abetting', 'wage', 'waging', 'war', 'the', 'waging or attempting to wage war or abetting waging of war against the government of india', 'or', 'the government of'],
    '121A': ['conspiracy', 'section', 'conspiracy to commit offences punishable by section 121', 'by', 'to', 'punishable', 'offences', '121', 'commit'],
    '122': ['the government', 'government of', 'government', 'intention', 'of', 'against', 'etc', 'collecting arms etc with intention of waging war against the government of india', 'india', 'waging', 'war', 'the', 'the government of', 'with', 'collecting', 'arms'],
    '123': ['the government', 'illegal', 'illegal omission', 'any illegal', 'design', 'to', 'government of', 'government', 'wage', 'war', 'concealing with intent to facilitate design to wage war', 'the government of', 'intent', 'with', 'facilitate', 'concealing', 'any illegal omission'],
    '124': ['any', 'lawful', 'to', 'of', 'president', 'exercise', 'etc', 'or', 'assaulting president governor etc with intent to compel or restrain the exercise of any lawful power', 'compel', 'assaulting', 'the', 'governor', 'power', 'with', 'intent', 'restrain'],
    '124A': ['sedition'],
    '125': ['the government', 'any', 'government of', 'waging war against any asiatic power in alliance with the government of india', 'government', 'of', 'against', 'india', 'war', 'waging', 'power', 'in', 'with', 'the', 'asiatic', 'the government of', 'alliance'],
    '126': ['the government', 'committing depredation on territories of power at peace with the government of india', 'with', 'government of', 'depredation', 'on', 'of', 'peace', 'government', 'committing', 'india', 'the', 'the government of', 'power', 'at', 'territories'],
    '127': ['by', 'any property', 'depredation', 'receiving property taken by war or depredation', 'any property knowing', 'war', 'taken', 'property knowing', 'or', 'property', 'receiving'],
    '128': ['allowing', 'prisoner', 'voluntarily', 'state', 'to', 'a public servant', 'of', 'public servant and', 'public servant voluntarily allowing prisoner of state or war to escape', 'public servant', 'or', 'escape', 'war', 'public', 'servant', 'a public servant and'],
    '129': ['prisoner', 'to', 'a public servant', 'public servant and', 'negligently', 'public servant negligently suffering such prisoner to escape', 'public servant', 'such', 'escape', 'public', 'servant', 'a public servant and', 'suffering'],
    '130': ['prisoner', 'harbouring', 'aiding escape of rescuing or harbouring such prisoner', 'of', 'such', 'escape', 'rescuing', 'or', 'aiding'],
    '141': ['unlawful', 'assembly', 'unlawful assembly', 'offense'],
    '142': ['unlawful', 'of', 'an unlawful assembly', 'being', 'assembly', 'being member of unlawful assembly', 'member', 'unlawful assembly', 'an unlawful'],
    '143': ['unlawful assembly', 'illegal gathering', 'prohibited assembly', 'unlawful group', 'illegal meeting'],
    '144': ['weapon', 'cause death', 'armed', 'unlawful', 'joining unlawful assembly armed with deadly weapon', 'assembly', 'deadly', 'with', 'joining', 'death'],
    '145': ['has', 'to', 'joining or continuing in unlawful assembly knowing it has been commanded to disperse', 'commanded', 'unlawful', 'an unlawful assembly', 'knowing', 'disperse', 'assembly', 'continuing', 'in', 'been', 'it', 'or', 'joining', 'unlawful assembly', 'an unlawful'],
    '146': ['unlawful', 'an unlawful assembly', 'rioting', 'unlawful assembly', 'an unlawful'],
    '147': ['rioting', 'riot', 'violent protest', 'mob violence', 'violent disorder', 'public disturbance', 'violent crowd'],
    '148': ['weapon', 'cause death', 'armed', 'rioting', 'deadly', 'with', 'rioting armed with deadly weapon', 'death'],
    '149': ['prosecution', 'common', 'of', 'unlawful', 'every', 'object', 'every member of unlawful assembly guilty of offence committed in prosecution of common object', 'an unlawful assembly', 'offence', 'assembly', 'committed', 'in', 'member', 'guilty', 'unlawful assembly', 'an unlawful'],
    '150': ['to', 'of', 'unlawful', 'conniving', 'hiring', 'any unlawful', 'persons', 'assembly', 'join', 'any unlawful assembly', 'at', 'or', 'unlawful assembly', 'hiring or conniving at hiring of persons to join unlawful assembly'],
    '151': ['has', 'knowingly', 'more', 'to', 'commanded', 'of', 'persons', 'after', 'disperse', 'assembly', 'knowingly joining or continuing in assembly of five or more persons after it has been commanded to disperse', 'continuing', 'in', 'five', 'it', 'or', 'been', 'joining'],
    '152': ['suppressing', 'public', 'obstructing', 'assault', 'etc', 'assaulting or obstructing public servant when suppressing riot etc', 'public servant', 'when', 'to assault', 'any public servant in', 'public servant in', 'assaulting', 'any public servant', 'or', 'threat', 'riot', 'servant'],
    '153': ['illegal', 'wantonly giving provocation with intent to cause riot', 'to', 'is illegal', 'wantonly', 'giving', 'cause', 'provocation', 'with', 'intent', 'riot'],
    '153A': ['promoting enmity between groups', 'hate speech', 'communal hatred', 'religious disharmony', 'inciting hatred', 'promoting disharmony'],
    '153B': ['to', 'imputations', 'assertions', 'integration', 'imputations assertions prejudicial to national integration', 'national', 'prejudicial'],
    '154': ['on', 'of', 'unlawful', 'which', 'is', 'unlawful assembly', 'land', 'owner', 'any unlawful', 'assembly', 'owner or occupier of land on which an unlawful assembly is held', 'any unlawful assembly', 'an', 'or', 'held', 'occupier'],
    '155': ['whose', 'benefit', 'of', 'liability', 'person', 'is', 'for', 'committed', 'riot', 'liability of person for whose benefit riot is committed'],
    '156': ['whose', 'benefit', 'of', 'liability', 'agent', 'is', 'owner', 'for', 'committed', 'or', 'liability of agent of owner or occupier for whose benefit riot is committed', 'riot', 'occupier'],
    '157': ['harbouring', 'unlawful', 'hired', 'persons', 'for', 'assembly', 'an', 'harbouring persons hired for an unlawful assembly'],
    '158': ['to', 'being hired to take part in an unlawful assembly or riot', 'unlawful', 'hired', 'take', 'part', 'being', 'assembly', 'in', 'an', 'or', 'riot'],
    '159': ['affray'],
    '160': ['affray', 'public fight', 'fighting in public', 'public disturbance', 'brawl', 'public violence'],
    '166': ['any', 'public servant disobeying law with intent to cause injury to any person', 'disobeying', 'public', 'to', 'a public servant', 'person', 'law', 'injury', 'public servant', 'cause', 'with', 'intent', 'servant'],
    '166A': ['public servant fails', 'disobeying', 'direction', 'a public servant fails', 'a public servant', 'under', 'law', 'of criminal', 'public servant disobeying direction under law', 'public servant', 'of criminal procedure', 'criminal procedure', 'criminal', 'public', 'servant'],
    '166B': ['non', 'government', 'of', 'punishment', 'for', 'punishment for non treatment of victim', 'victim', 'central government', 'treatment'],
    '167': ['public servant framing an incorrect document with intent to cause injury', 'framing', 'with', 'to', 'document', 'a public servant', 'incorrect', 'any document', 'injury', 'public servant', 'any document or', 'document or', 'cause', 'an', 'public', 'intent', 'servant'],
    '168': ['a public servant', 'public servant', 'engaging', 'public servant unlawfully engaging in trade', 'unlawfully', 'in', 'public', 'public servant not', 'servant', 'trade', 'such public servant not'],
    '169': ['public servant unlawfully buying or bidding for property', 'bidding', 'buying', 'certain property', 'a public servant', 'public servant', 'or', 'for', 'unlawfully', 'public', 'property', 'servant'],
    '170': ['a public servant', 'public servant', 'personating a public servant', 'false', 'a', 'personating', 'public', 'servant'],
    '171': ['wearing garb or carrying token used by public servant with fraudulent intent', 'used', 'token', 'by', 'with', 'public', 'servant', 'public servant', 'wearing', 'intent', 'or', 'garb', 'fraudulent', 'carrying'],
    '186': ['obstructing public servant', 'preventing official duty', 'hindering public servant', 'obstructed officer', 'interfered with official'],
    '189': ['threat to public servant', 'threatened official', 'intimidated officer', 'threatened government employee'],
    '2': ['of', 'punishment', 'within', 'india', 'offences', 'committed', 'punishment of offences committed within india'],
    '299': ['death', 'culpable', 'death by', 'causes death', 'culpable homicide', 'homicide', 'causes death by'],
    '3': ['may', 'by', 'but', 'of', 'which', 'law', 'punishment', 'within', 'india', 'offences', 'beyond', 'committed', 'be', 'punishment of offences committed beyond but which by law may be tried within india', 'tried'],
    '300': ['is murder', 'is murder if', 'murder if', 'causing death', 'murder', 'death'],
    '302': ['murder', 'kill', 'death', 'homicide', 'fatal', 'deceased', 'died', 'dead', 'slain', 'assassinated', 'executed', 'strangled', 'suffocated', 'poisoned', 'shot dead', 'stabbed to death', 'beaten to death'],
    '304': ['culpable homicide', 'not murder', 'death', 'killed', 'unintentional', 'without premeditation', 'heat of passion', 'provocation', 'sudden fight'],
    '304A': ['death by negligence', 'accidental death', 'rash act', 'negligent act', 'careless', 'reckless', 'accident', 'unintentional', 'traffic accident', 'medical negligence'],
    '304B': ['dowry death', 'bride', 'marriage', 'dowry', 'harassment', 'suicide', 'unnatural death', 'burn', 'in-laws', 'husband'],
    '305': ['suicide', 'of', 'abetment', 'abetment of suicide'],
    '306': ['suicide', 'of', 'abetment', 'abetment of suicide'],
    '307': ['attempt to murder', 'attempted murder', 'try to kill', 'intent to kill', 'shot', 'stabbed', 'attacked', 'life threatening', 'attempted homicide', 'failed murder', 'tried to kill'],
    '308': ['to murder', 'attempt to culpable homicide', 'homicide', 'to', 'culpable', 'murder', 'attempt'],
    '309': ['suicide', 'attempt', 'attempt to suicide', 'to'],
    '312': ['causing miscarriage', 'a woman with', 'miscarriage', 'a woman', 'woman with', 'causing', 'woman'],
    '319': ['hurt'],
    '320': ['grievous hurt', 'hurt', 'grievous'],
    '321': ['voluntarily', 'hurt', 'causing hurt', 'causing', 'voluntarily causing hurt'],
    '322': ['voluntarily', 'hurt', 'causing', 'voluntarily causing grievous hurt', 'grievous hurt', 'grievous'],
    '323': ['hurt', 'injury', 'assault', 'beat', 'hit', 'slap', 'punch', 'wound', 'bruise', 'physical harm', 'bodily harm', 'attacked', 'physical assault', 'voluntarily causing hurt'],
    '324': ['hurt by dangerous weapon', 'knife', 'sharp weapon', 'dangerous weapon', 'cut', 'stab', 'slash', 'weapon', 'iron rod', 'acid', 'burn', 'grievous', 'serious injury'],
    '325': ['grievous hurt', 'serious injury', 'fracture', 'disfiguration', 'permanent damage', 'disability', 'severe', 'grievous', 'broken bone', 'loss of vision', 'loss of hearing'],
    '326': ['grievous hurt by dangerous weapon', 'acid attack', 'serious injury with weapon', 'permanent damage', 'disfiguration with weapon', 'grievous with dangerous weapon'],
    '326A': ['acid attack', 'hurt', 'attack', 'grievous hurt by', 'hurt by', 'acid', 'grievous hurt'],
    '326B': ['to', 'attack', 'acid', 'attempt', 'attempt to acid attack'],
    '327': ['an illegal', 'extort property', 'extort', 'voluntarily', 'hurt', 'illegal', 'to', 'an illegal act', 'causing', 'causing hurt to', 'hurt to', 'illegal act', 'causing hurt', 'voluntarily causing hurt to extort property', 'property', 'property or', 'extort property or'],
    '328': ['hurt', 'by', 'causing', 'causing hurt by', 'hurt by', 'causing hurt by poison', 'causing hurt', 'poison'],
    '329': ['an illegal', 'extort property', 'voluntarily', 'extort', 'hurt', 'illegal', 'to', 'an illegal act', 'grievous hurt to', 'causing', 'hurt to', 'voluntarily causing grievous hurt to extort property', 'illegal act', 'property or', 'grievous hurt', 'property', 'grievous', 'extort property or'],
    '334': ['hurt on', 'voluntarily', 'hurt', 'on', 'causing hurt on', 'causing hurt', 'causing', 'voluntarily causing hurt on provocation', 'provocation'],
    '335': ['hurt on', 'voluntarily', 'hurt', 'on', 'grievous hurt on', 'causing', 'provocation', 'grievous hurt', 'voluntarily causing grievous hurt on provocation', 'grievous'],
    '336': ['personal', 'act', 'endangering', 'life', 'or', 'act endangering life or personal safety', 'safety'],
    '337': ['hurt', 'by', 'act', 'endangering', 'causing hurt by act endangering life', 'causing hurt', 'causing', 'causing hurt by', 'hurt by', 'life'],
    '338': ['causing grievous hurt by act endangering life', 'hurt', 'by', 'act', 'endangering', 'causing', 'grievous hurt by', 'hurt by', 'life', 'grievous hurt', 'grievous'],
    '339': ['wrongful', 'restraint', 'wrongful restraint'],
    '340': ['wrongful confinement', 'wrongful', 'confinement'],
    '341': ['punishment for wrongful restraint', 'restraint', 'punishment', 'for', 'wrongful'],
    '342': ['punishment for wrongful confinement', 'punishment', 'confinement', 'for', 'wrongful'],
    '343': ['more', 'wrongful', 'days', 'confinement', 'for', 'wrongful confinement for three or more days', 'or', 'three'],
    '344': ['more', 'days', 'wrongful confinement for ten or more days', 'ten', 'confinement', 'for', 'or', 'wrongful'],
    '346': ['wrongful confinement in secret', 'confinement', 'secret', 'in', 'wrongful'],
    '350': ['force', 'criminal force', 'criminal'],
    '351': ['assault', 'criminal force', 'that criminal', 'criminal', 'that criminal force'],
    '352': ['for assault or', 'assault', 'force', 'or criminal', 'for assault', 'punishment', 'criminal force', 'for', 'punishment for assault or criminal force', 'criminal', 'or', 'or criminal force', 'assault or'],
    '354': ['assault on woman', 'modesty', 'touch', 'outrage', 'female', 'inappropriate touching', 'harassment', 'molestation', 'groping', 'sexual harassment', 'forcibly', 'disrobe', 'unwanted advances'],
    '354A': ['sexual', 'sexual harassment and', 'harassment', 'for sexual harassment', 'sexual harassment', 'harassment and', 'for sexual'],
    '354B': ['assault with intent to disrobe', 'to woman', 'to woman with', 'to', 'woman', 'assault', 'of criminal', 'disrobe', 'criminal force', 'woman with', 'of criminal force', 'criminal', 'with', 'intent', 'assault or'],
    '354C': ['a woman', 'a woman engaging', 'voyeurism', 'woman', 'woman engaging'],
    '354D': ['a woman', 'woman', 'a woman and', 'stalking', 'woman and'],
    '359': ['kidnapping', 'kidnap'],
    '363': ['kidnapping', 'abduction', 'minor', 'child', 'taken away', 'forcibly taken', 'missing person', 'abducted', 'kidnapped', 'taken without consent'],
    '363A': ['kidnapping', 'maiming', 'for', 'kidnapping or maiming a minor for begging', 'a', 'minor', 'kidnap', 'or', 'begging'],
    '366': ['kidnapping woman', 'abduction of woman', 'compel marriage', 'forced marriage', 'illicit intercourse', 'forced to marry', 'abducted woman', 'kidnapped for marriage'],
    '366A': ['girl', 'procuration of minor girl', 'of', 'procuration', 'minor'],
    '366B': ['foreign', 'girl', 'from', 'importation', 'of', 'country', 'importation of girl from foreign country'],
    '370': ['trafficking of person', 'of', 'person', 'trafficking'],
    '370A': ['of', 'trafficked', 'person', 'exploitation', 'a', 'exploitation of a trafficked person'],
    '375': ['sexual intercourse', 'sexual', 'a woman against', 'a woman', 'woman against', 'woman', 'rape'],
    '376': ['rape', 'sexual assault', 'forced intercourse', 'without consent', 'sexual violence', 'violated', 'sexual abuse', 'non-consensual', 'sexual offence', 'penetration without consent'],
    '376A': ['state', 'of victim during', 'of victim', 'causing death or', 'causing death resulting in persistent vegetative state', 'causing death', 'causing', 'victim during', 'persistent', 'in', 'victim', 'death or', 'resulting', 'during rape', 'vegetative', 'death', 'rape'],
    '376B': ['wife', 'separation', 'intercourse', 'by', 'during', 'sexual intercourse by husband upon his wife during separation', 'sexual intercourse', 'sexual', 'husband', 'upon', 'his'],
    '376C': ['intercourse', 'by', 'sexual intercourse', 'sexual', 'person', 'sexual intercourse by a person in authority', 'a', 'in', 'authority'],
    '376D': ['a woman is', 'gang', 'woman is', 'a woman', 'woman', 'rape', 'gang rape'],
    '376E': ['repeat offenders', 'offenders', 'repeat', 'rape', 'of rape'],
    '378': ['theft', 'stealing', 'dishonestly take', 'movable property', 'without consent', 'took property', 'dishonest intention'],
    '379': ['theft', 'steal', 'stolen', 'took', 'property', 'belongings', 'missing', 'robbed', 'pickpocket', 'shoplifting', 'snatched', 'dishonestly took', 'stole from person'],
    '380': ['theft in dwelling', 'house theft', 'home burglary', 'break-in', 'house', 'dwelling', 'home', 'break', 'burglary', 'residence', 'apartment', 'stole from house', 'entered house to steal'],
    '381': ['theft by servant', 'employee theft', 'domestic help theft', 'servant stole', 'worker theft', 'staff theft', 'employee stole', 'domestic worker'],
    '382': ['theft after preparation to cause death', 'dangerous theft', 'armed theft', 'theft with weapon', 'prepared to hurt', 'theft with violence'],
    '383': ['of injury', 'extortion', 'commit extortion', 'injury', 'of injury to', 'injury to'],
    '384': ['extortion', 'threat', 'blackmail', 'demand', 'money', 'coercion', 'forced', 'pay up', 'threatening for money', 'forced to pay', 'illegal demand', 'under threat'],
    '385': ['of injury', 'of', 'extortion', 'person', 'commit extortion', 'injury', 'injury in', 'fear', 'of injury in', 'putting', 'in', 'putting person in fear of injury'],
    '386': ['extortion by putting in fear of death', 'death threat for money', 'extortion with deadly threat', 'pay or die', 'life threatening extortion'],
    '387': ['putting person in fear of death', 'of death', 'hurt', 'of', 'of death or', 'person', 'extortion', 'commit extortion', 'fear', 'putting', 'in', 'death or', 'grievous hurt', 'death'],
    '388': ['accusation', 'extortion by threat of accusation', 'by threat', 'by', 'extortion by', 'extortion', 'of', 'threat of', 'death or', 'with death or', 'threat', 'by threat of', 'with death', 'death'],
    '389': ['accusation', 'putting person in fear of accusation', 'of', 'person', 'fear', 'putting', 'in', 'death or', 'with death or', 'with death', 'death'],
    '390': ['robbery', 'theft with force', 'forceful theft', 'violent theft', 'snatching with force'],
    '391': ['robbery', 'dacoity', 'a robbery'],
    '392': ['robbery', 'force', 'threat', 'weapon', 'steal', 'property', 'violence', 'forcibly took', 'snatched', 'mugging', 'armed robbery', 'violent theft', 'forceful stealing'],
    '393': ['to', 'robbery', 'commit robbery', 'attempt to commit robbery', 'commit', 'attempt'],
    '394': ['voluntarily', 'committing robbery', 'hurt', 'robbery', 'committing', 'causing', 'in', 'hurt in', 'causing hurt', 'voluntarily causing hurt in committing robbery', 'causing hurt in'],
    '395': ['dacoity', 'gang robbery', 'armed gang', 'robbery', 'group', 'five', 'persons', 'bandits', 'gang of thieves', 'armed group robbery', 'five or more robbers'],
    '396': ['dacoity', 'with murder', 'murder', 'with', 'dacoity with murder'],
    '397': ['robbery with deadly weapon', 'armed robbery', 'robbery with gun', 'robbery with knife', 'deadly weapon during robbery'],
    '398': ['robbery with attempt to cause death', 'deadly robbery', 'attempted murder during robbery', 'life-threatening robbery'],
    '399': ['to', 'making preparation to commit dacoity', 'dacoity', 'commit', 'making', 'preparation'],
    '4': ['to', 'extension', 'of', 'territorial', 'extra', 'offences', 'code', 'extension of code to extra territorial offences'],
    '402': ['of', 'committing', 'dacoity', 'purpose', 'for', 'assembling for purpose of committing dacoity', 'assembling'],
    '403': ['dishonest misappropriation of', 'dishonest', 'misappropriation of', 'misappropriation', 'of', 'dishonest misappropriation of property', 'of property', 'dishonest misappropriation', 'property'],
    '404': ['dishonest misappropriation of', 'dishonest misappropriation of property of deceased person', 'dishonest', 'misappropriation of', 'misappropriation', 'of', 'person', 'property possessed', 'dishonest misappropriation', 'of property', 'his death', 'deceased', 'of property possessed', 'property', 'death'],
    '405': ['criminal breach of trust', 'breach', 'of', 'trust', 'of trust', 'criminal breach of', 'breach of', 'criminal breach', 'criminal'],
    '406': ['criminal breach of trust', 'misappropriation', 'property', 'dishonest', 'entrusted', 'embezzlement', 'misused funds', 'dishonestly used', 'entrusted property', 'betrayed trust', 'fiduciary breach'],
    '407': ['trust by', 'breach', 'by', 'of', 'criminal breach of trust by carrier', 'trust', 'of trust', 'criminal breach of', 'breach of', 'criminal breach', 'criminal', 'of trust by', 'carrier'],
    '408': ['trust by', 'breach', 'by', 'criminal breach of trust by clerk or servant', 'of', 'trust', 'of trust', 'criminal breach of', 'breach of', 'criminal breach', 'of trust by', 'clerk', 'criminal', 'or', 'servant'],
    '409': ['breach of trust by public servant', 'government employee fraud', 'official misappropriation', 'public servant embezzlement', 'government funds misuse'],
    '410': ['stolen', 'property', 'stolen property'],
    '411': ['stolen', 'dishonestly receiving stolen property', 'stolen property', 'dishonestly', 'property', 'receiving'],
    '412': ['stolen', 'property stolen', 'dishonestly receiving property stolen in dacoity', 'receiving property', 'dacoity', 'receiving property stolen', 'dishonestly', 'in', 'property', 'receiving'],
    '413': ['stolen', 'habitually', 'stolen property', 'dealing', 'habitually dealing in stolen property', 'in', 'property'],
    '414': ['stolen', 'of', 'concealment', 'stolen property', 'assisting', 'in', 'assisting in concealment of stolen property', 'property'],
    '415': ['cheating', 'deception', 'fraud', 'deceive', 'fraudulently', 'misrepresentation', 'false promise', 'dishonest inducement'],
    '416': ['personation', 'cheating by personation', 'cheating', 'by'],
    '417': ['punishment for cheating', 'cheating', 'punishment', 'for cheating', 'for'],
    '418': ['that', 'may', 'loss', 'cheating with knowledge that wrongful loss may ensue', 'cheating', 'ensue', 'knowledge', 'cheating with', 'with', 'wrongful'],
    '419': ['by', 'cheating by', 'personation', 'cheating', 'punishment', 'punishment for cheating by personation', 'for', 'for cheating', 'for cheating by'],
    '420': ['cheating', 'fraud', 'deceive', 'dishonest', 'scam', 'false', 'misrepresentation', 'fraudulent', 'defrauded', 'duped', 'swindled', 'fake', 'counterfeit', 'ponzi scheme', 'fraudulent scheme'],
    '421': ['dishonest', 'dishonest or fraudulent removal or concealment of property', 'of', 'removal', 'concealment', 'of property to', 'fraud', 'property', 'of property', 'or', 'property to', 'fraudulent'],
    '422': ['dishonestly or fraudulently preventing debt being available', 'debt', 'preventing', 'fraudulently', 'being', 'available', 'fraud', 'dishonestly', 'or'],
    '423': ['dishonest', 'false statement', 'of', 'deed', 'transfer', 'dishonest or fraudulent execution of deed of transfer', 'containing false', 'false', 'fraudulent', 'fraud', 'containing false statement', 'or', 'execution'],
    '424': ['dishonest', 'dishonest or fraudulent removal or concealment of property', 'of', 'removal', 'concealment', 'fraud', 'property', 'of property', 'or', 'fraudulent'],
    '425': ['damage to', 'damage', 'or damage to', 'or damage', 'mischief'],
    '426': ['for', 'punishment for mischief', 'punishment', 'mischief'],
    '427': ['damage to', 'mischief causing damage', 'causing damage to', 'damage', 'causing', 'causing damage', 'mischief'],
    '428': ['mischief by killing or maiming animal', 'by', 'maiming', 'kill', 'or', 'killing', 'animal', 'mischief'],
    '429': ['by', 'maiming', 'mischief by killing or maiming cattle', 'kill', 'or', 'killing', 'cattle', 'mischief'],
    '430': ['mischief by injury to works of irrigation', 'by', 'to', 'of', 'by injury', 'works', 'irrigation', 'injury', 'by injury to', 'injury to', 'mischief'],
    '431': ['mischief by injury to public road', 'by', 'to', 'by injury', 'injury', 'road', 'by injury to', 'injury to', 'public', 'mischief'],
    '434': ['by', 'mischief by destroying or moving landmark', 'moving', 'destroying', 'landmark', 'or', 'mischief'],
    '435': ['mischief by fire or explosive substance', 'by', 'cause damage', 'explosive', 'fire', 'damage', 'or', 'substance', 'mischief'],
    '436': ['house', 'by', 'with', 'to', 'destroy', 'mischief by fire or explosive substance with intent to destroy house', 'explosive', 'fire', 'or', 'intent', 'substance', 'mischief'],
    '437': ['destroy', 'to', 'vessel', 'with', 'intent', 'mischief with intent to destroy vessel', 'mischief'],
    '438': ['by', 'with', 'to', 'destroy', 'mischief by fire or explosive substance with intent to destroy vessel', 'explosive', 'fire', 'vessel', 'or', 'intent', 'substance', 'mischief'],
    '439': ['theft', 'commit theft', 'punishment', 'intentionally', 'for', 'running', 'vessel', 'punishment for intentionally running vessel aground', 'aground'],
    '440': ['hurt', 'causing death or', 'after', 'for', 'causing death', 'causing', 'committed', 'mischief committed after preparation made for causing death', 'death or', 'made', 'or hurt', 'preparation', 'death', 'mischief'],
    '441': ['criminal trespass', 'unlawful entry', 'illegal entry', 'entered property', 'without permission', 'unauthorized entry'],
    '447': ['criminal trespass', 'trespass', 'unlawful entry', 'entered property', 'unauthorized access', 'illegal entry'],
    '448': ['house trespass', 'break into house', 'entered home', 'house breaking', 'unlawful home entry', 'trespass into dwelling'],
    '449': ['house', 'to', 'trespass', 'house trespass in order to commit offence punishable with death', 'offence', 'punishable', 'trespass in', 'commit', 'order', 'in', 'with', 'with death', 'death'],
    '450': ['imprisonment', 'house', 'to', 'trespass', 'offence', 'punishable', 'for', 'commit', 'order', 'in', 'life', 'with', 'house trespass in order to commit offence punishable with imprisonment for life', 'trespass in'],
    '451': ['house', 'to', 'trespass', 'offence', 'house trespass in order to commit offence', 'commit', 'order', 'in', 'trespass in'],
    '452': ['house', 'hurt', 'assault', 'house trespass after preparation for hurt assault or wrongful restraint', 'trespass after', 'trespass', 'after', 'restraint', 'for', 'for hurt', 'or', 'wrongful', 'assault or', 'preparation'],
    '453': ['house', 'lurking', 'breaking', 'trespass or', 'punishment for lurking house trespass or house breaking', 'trespass', 'punishment', 'for', 'or'],
    '454': ['house breaking', 'break-in', 'burglary', 'broke into house', 'forced entry', 'house trespass for offense'],
    '455': ['house', 'hurt', 'lurking', 'breaking', 'trespass or', 'assault', 'trespass', 'after', 'for hurt', 'for', 'lurking house trespass or house breaking after preparation for hurt', 'or', 'assault or', 'preparation'],
    '456': ['house', 'by', 'lurking', 'breaking', 'trespass or', 'night', 'trespass', 'punishment', 'for', 'punishment for lurking house trespass or house breaking by night', 'or'],
    '457': ['house breaking at night', 'night burglary', 'break-in at night', 'night-time house trespass', 'nocturnal break-in'],
    '458': ['house', 'by', 'lurking', 'breaking', 'hurt', 'trespass or', 'night', 'assault', 'trespass', 'after', 'for hurt', 'for', 'lurking house trespass or house breaking by night after preparation for hurt', 'or', 'preparation'],
    '459': ['grievous hurt caused', 'grievous hurt caused whilst committing lurking house trespass or house breaking', 'hurt', 'house', 'lurking', 'breaking', 'trespass or', 'grievous hurt', 'hurt caused', 'committing', 'grievous', 'trespass', 'or', 'whilst', 'caused'],
    '460': ['trespass', 'death or grievous hurt caused by one of several persons', 'caused', 'grievous hurt caused', 'one', 'hurt', 'by', 'of', 'death', 'several', 'trespass or', 'death or', 'or', 'grievous hurt', 'where death or', 'hurt caused', 'persons', 'where death', 'grievous'],
    '463': ['forgery', 'fake document', 'false document', 'forged', 'counterfeit document', 'fraudulent document', 'document fraud'],
    '465': ['punishment for forgery', 'forged document', 'fake document', 'false document', 'document fraud'],
    '468': ['forgery for cheating', 'forged document for fraud', 'fake document for deception', 'fraudulent document for cheating'],
    '471': ['using forged document', 'used fake document', 'submitted false document', 'presented forged document', 'relied on counterfeit document'],
    '489A': ['counterfeiting currency', 'fake money', 'counterfeit notes', 'forged currency', 'fake currency', 'counterfeit coins'],
    '493': ['cohabitation by deceit', 'false marriage', 'fraudulent marriage', 'deceived into marriage', 'fake marriage'],
    '494': ['bigamy', 'second marriage', 'married again', 'multiple spouses', 'two wives', 'two husbands'],
    '498A': ['cruelty by husband or relatives', 'domestic violence', 'dowry harassment', 'marital cruelty', 'husband harassment', 'in-laws harassment', 'wife beating', 'domestic abuse', 'matrimonial cruelty'],
    '499': ['defamation', 'slander', 'libel', 'damaged reputation', 'false statement', 'character assassination', 'defamatory statement'],
    '5': ['the government', 'affected', 'by', 'to', 'laws', 'certain laws not to be affected by this act', 'government', 'government of', 'act', 'this', 'certain', 'not', 'be', 'the government of'],
    '500': ['punishment for defamation', 'defamed', 'slandered', 'libeled', 'damaged reputation', 'defamatory'],
    '503': ['criminal intimidation', 'threatening', 'threat', 'intimidation', 'threatened harm', 'threatened injury'],
    '504': ['intentional insult', 'provocation', 'breach of peace', 'insulted', 'provoked', 'abused verbally', 'verbal abuse', 'insulting language', 'provocative words', 'incitement'],
    '505': ['to', 'statements conducing to public mischief', 'conducing', 'statements', 'public', 'mischief'],
    '506': ['criminal intimidation', 'threat', 'threatening', 'intimidation', 'threatened', 'fear', 'danger', 'death threat', 'threatened harm', 'threatened injury', 'threatened violence'],
    '507': ['criminal intimidation by anonymous communication', 'anonymous threat', 'threatening letter', 'anonymous intimidation'],
    '508': ['will', 'that', 'to', 'person', 'inducing', 'caused', 'rendered', 'by', 'he', 'of', 'act', 'believe', 'an', 'displeasure', 'act caused by inducing person to believe that he will be rendered an object of the divine displeasure', 'be', 'divine', 'object', 'the'],
    '509': ['insult to modesty of woman', 'obscene gesture', 'lewd comment', 'vulgar remark', 'sexual harassment', 'eve teasing', 'indecent behavior', 'obscene act', 'insulted woman'],
    '510': ['drunken', 'by', 'misconduct in public by a drunken person', 'person', 'a', 'in', 'misconduct', 'public'],
    '511': ['attempting to commit offense', 'attempted crime', 'tried to commit', 'attempt to commit', 'unsuccessful attempt'],
    '66': ['computer related offense', 'hacking', 'data theft', 'unauthorized access', 'computer fraud', 'cyber crime'],
    '66A': ['offensive electronic message', 'threatening email', 'abusive message', 'harassing online', 'offensive communication'],
    '66C': ['identity theft', 'stolen password', 'impersonation online', 'digital identity theft', 'electronic signature theft'],
    '66D': ['cheating by impersonation using computer', 'online impersonation', 'fake profile', 'digital impersonation', 'electronic fraud'],
    '66E': ['privacy violation', 'private image', 'unauthorized image capture', 'privacy breach', 'private area photograph'],
    '66F': ['cyber terrorism', 'digital attack', 'computer system attack', 'critical infrastructure attack', 'cyber attack'],
    '67': ['publishing obscene material', 'obscene content', 'pornographic content', 'indecent material online', 'electronic obscenity'],
    '67A': ['publishing sexually explicit content', 'electronic pornography', 'explicit digital content', 'sexual content online'],
    '67B': ['child pornography', 'minor explicit content', 'child sexual abuse material', 'underage explicit content'],
    '76': ['by', 'act', 'person', 'law', 'done', 'bound', 'a', 'act done by a person bound by law'],
    '77': ['acting', 'judicially', 'act of judge when acting judicially', 'of', 'act', 'when', 'judge'],
    '78': ['pursuant', 'to', 'act done pursuant to the judgment or order of court', 'of', 'court', 'act', 'done', 'the', 'order', 'or', 'judgment'],
    '79': ['by', 'act', 'person', 'law', 'act done by a person justified by law', 'done', 'a', 'justified'],
    '80': ['accident', 'accident in doing a lawful act', 'any criminal', 'lawful', 'act', 'doing', 'a', 'in', 'criminal', 'any criminal intention', 'criminal intention'],
    '81': ['to', 'but', 'act', 'without', 'act likely to cause harm but done without criminal intent', 'likely', 'done', 'criminal', 'harm', 'cause', 'intent'],
    '82': ['seven', 'of', 'child', 'act', 'under', 'age', 'years', 'a', 'act of a child under seven years of age'],
    '83': ['and', 'seven', 'of', 'child', 'act', 'under', 'a', 'twelve', 'act of a child above seven and under twelve', 'above'],
    '84': ['act of a person of unsound mind', 'of', 'unsound', 'act', 'person', 'mind', 'a'],
    '85': ['will', 'by', 'reason', 'of', 'act', 'person', 'against', 'a', 'act of a person incapable of judgment by reason of intoxication caused against his will', 'incapable', 'intoxication', 'caused', 'judgment', 'his'],
    '86': ['one', 'by', 'is', 'offence requiring a particular intent or knowledge committed by one who is intoxicated', 'offence', 'a', 'knowledge', 'particular', 'committed', 'who', 'or', 'intent', 'intoxicated', 'requiring'],
    '87': ['and', 'hurt', 'to', 'cause death', 'grievous hurt', 'act', 'grievous', 'likely', 'not', 'cause death or', 'be', 'cause', 'death or', 'known', 'or', 'act not intended and not known to be likely to cause death or grievous hurt', 'death', 'intended'],
    '88': ['by', 'to', 'cause death', 'act', 'not', 'done', 'cause', 'consent', 'act not intended to cause death done by consent', 'death', 'intended'],
    '89': ['insane', 'good', 'benefit', 'of', 'child', 'act', 'person', 'faith', 'for', 'done', 'act done in good faith for benefit of child or insane person', 'in', 'or'],
    '90': ['of injury', 'to', 'under', 'given', 'injury', 'fear', 'misconception', 'consent known to be given under fear or misconception', 'be', 'known', 'or', 'consent'],
    '91': ['acts', 'of', 'which', 'exclusion', 'offences', 'independently', 'exclusion of acts which are offences independently of harm caused', 'are', 'harm', 'caused'],
    '92': ['good', 'benefit', 'of', 'act', 'person', 'without', 'faith', 'for', 'done', 'act done in good faith for benefit of a person without consent', 'a', 'in', 'consent'],
    '93': ['good', 'faith', 'in', 'communication', 'communication made in good faith', 'made'],
    '94': ['by', 'to', 'is', 'act', 'which', 'person', 'threats', 'a', 'compelled', 'act to which a person is compelled by threats', 'murder', 'except murder', 'threat', 'with death', 'death'],
    '95': ['slight', 'act', 'act causing slight harm', 'causing', 'harm'],
    '96': ['private', 'things', 'done', 'things done in private defence', 'in', 'defence'],
    '97': ['body', 'and', 'of', 'private', 'right of private defence of the body and of property', 'right', 'the', 'defence', 'property'],
    '98': ['of', 'unsound', 'against', 'private', 'act', 'person', 'mind', 'right', 'the', 'a', 'defence', 'right of private defence against the act of a person of unsound mind'],
    '99': ['no', 'acts', 'of death', 'hurt', 'is', 'of', 'against', 'which', 'private', 'acts against which there is no right of private defence', 'of death or', 'grievous hurt', 'right', 'there', 'death or', 'defence', 'death'],
}

def preprocess_text(text):
    """
    Preprocess the text by correcting common misspellings, removing special characters,
    converting to lowercase, tokenizing, removing stopwords, and lemmatizing
    """
    if not text:
        return ""

    try:
        # Convert to lowercase
        text = text.lower()

        # Correct common misspellings related to crimes
        common_misspellings = {
            # Murder related
            'muder': 'murder',
            'mudered': 'murdered',
            'murderd': 'murdered',
            'murdred': 'murdered',
            'homocide': 'homicide',
            'homocid': 'homicide',
            'killd': 'killed',
            'kiled': 'killed',

            # Assault related
            'asault': 'assault',
            'asaulted': 'assaulted',
            'asaulting': 'assaulting',
            'atack': 'attack',
            'atacked': 'attacked',
            'beeting': 'beating',
            'beet': 'beat',
            'hiting': 'hitting',
            'hited': 'hit',

            # Stabbing related
            'stabing': 'stabbing',
            'stabed': 'stabbed',
            'stabd': 'stabbed',
            'nife': 'knife',

            # Theft related
            'theif': 'thief',
            'theift': 'theft',
            'steeling': 'stealing',
            'stole': 'stole',
            'stoled': 'stolen',

            # Robbery related
            'roberry': 'robbery',
            'robed': 'robbed',
            'robing': 'robbing',

            # Harassment related
            'harasment': 'harassment',
            'harased': 'harassed',
            'harrasing': 'harassing',
            'stalking': 'stalking',
            'stalked': 'stalked',

            # Defamation related
            'defamation': 'defamation',
            'defamed': 'defamed',
            'slander': 'slander',
            'slanderd': 'slandered',

            # Cheating related
            'cheeted': 'cheated',
            'cheeting': 'cheating',
            'frauded': 'defrauded',
            'scamed': 'scammed',
            'deceved': 'deceived',

            # Kidnapping related
            'kidnaped': 'kidnapped',
            'kidnapin': 'kidnapping',
            'abducted': 'abducted',
            'abduct': 'abduct',

            # Sexual crimes related
            'raped': 'raped',
            'raping': 'raping',
            'molested': 'molested',
            'molesting': 'molesting',
            'sexualy': 'sexually',

            # Extortion related
            'extorting': 'extorting',
            'extorted': 'extorted',
            'blackmaled': 'blackmailed',
            'threatend': 'threatened',
            'threatning': 'threatening',

            # Corruption related
            'bribery': 'bribery',
            'bribed': 'bribed',

            # Document fraud related
            'forgery': 'forgery',
            'forged': 'forged',
            'signatur': 'signature',

            # Trespass related
            'tresspas': 'trespass',
            'tresspased': 'trespassed',
            'broke in': 'broke in',

            # Damage related
            'damagd': 'damaged',
            'destroyd': 'destroyed',
            'vandalizd': 'vandalized'
        }

        # Replace misspelled words
        for misspelled, correct in common_misspellings.items():
            text = re.sub(r'\b' + misspelled + r'\b', correct, text)

        # Remove special characters
        text = re.sub(r'[^\w\s]', ' ', text)

        try:
            # Try to tokenize with NLTK
            tokens = word_tokenize(text)
        except Exception as tokenize_error:
            logger.warning(f"Error tokenizing with NLTK: {str(tokenize_error)}")
            # Simple fallback tokenization
            tokens = text.split()

        # Remove stopwords and lemmatize
        try:
            # Process tokens one by one to isolate any problematic tokens
            processed_tokens = []
            for token in tokens:
                if token not in stop_words:
                    try:
                        lemmatized = lemmatizer.lemmatize(token)
                        processed_tokens.append(lemmatized)
                    except Exception as token_error:
                        logger.warning(f"Error lemmatizing token '{token}': {str(token_error)}")
                        # If lemmatization fails for a specific token, use the original token
                        processed_tokens.append(token)
        except Exception as lemmatize_error:
            logger.warning(f"Error in lemmatization process: {str(lemmatize_error)}")
            # Fallback to just removing stopwords
            processed_tokens = [token for token in tokens if token not in stop_words]

        return ' '.join(processed_tokens)
    except Exception as e:
        logger.error(f"Error in text preprocessing: {str(e)}")
        # Return simplified text as fallback
        return text.lower()

def extract_features(text):
    """Extract features from the text using TF-IDF vectorization"""
    try:
        # Load the vectorizer if it exists
        if os.path.exists(VECTORIZER_PATH):
            with open(VECTORIZER_PATH, 'rb') as f:
                vectorizer = pickle.load(f)
            return vectorizer.transform([preprocess_text(text)])
        else:
            # If no vectorizer exists, create a simple one
            vectorizer = TfidfVectorizer(max_features=5000)
            vectorizer.fit([preprocess_text(text)])

            # Save the vectorizer for future use
            with open(VECTORIZER_PATH, 'wb') as f:
                pickle.dump(vectorizer, f)

            return vectorizer.transform([preprocess_text(text)])
    except Exception as e:
        logger.error(f"Error extracting features: {str(e)}")
        return None

def keyword_based_analysis(text):
    """
    Analyze the complaint text using keyword matching to identify potential IPC sections.
    This is a fallback method when ML model is not available.
    """
    text = text.lower()
    matches = {}

    # Common words to ignore (to reduce false positives)
    common_words = ['a', 'an', 'the', 'of', 'in', 'on', 'at', 'by', 'to', 'for', 'with', 'from', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could']

    # Track matched keywords for each section
    matched_keywords = {}

    for section, keywords in IPC_KEYWORDS.items():
        score = 0
        section_matched_keywords = []

        for keyword in keywords:
            # Skip common words that are likely to cause false matches
            if keyword in common_words or len(keyword) <= 2:
                continue

            # Check for exact word match with word boundaries
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                # Give higher weight to multi-word keywords
                keyword_weight = 1.0
                if ' ' in keyword:
                    keyword_weight = 2.0  # Multi-word matches are more significant

                score += keyword_weight
                section_matched_keywords.append(keyword)

        # Only consider sections with significant matches
        if score >= 2.0 or (score > 0 and len(section_matched_keywords) >= 2):
            # Calculate a confidence score (0-1) based on keyword matches
            # Adjust the formula to give more weight to sections with multiple matches
            confidence = min(score / (len(keywords) * 0.8), 1.0)
            matches[section] = confidence
            matched_keywords[section] = section_matched_keywords

    # Sort by confidence score and return top matches (limit to top 5)
    sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)[:5]

    # Add matched keywords to the result
    result = []
    for section, confidence in sorted_matches:
        result.append((section, confidence, matched_keywords.get(section, [])))

    return result

def train_model(training_data=None):
    """
    Train a machine learning model to classify complaints into IPC sections.
    If training_data is not provided, it will use a small default dataset.

    Args:
        training_data: A list of tuples (complaint_text, [ipc_sections])
    """
    try:
        # If no training data is provided, use a small default dataset
        if not training_data:
            # Enhanced dataset for better training
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

        # Extract texts and labels
        texts = [item[0] for item in training_data]
        labels = [item[1] for item in training_data]

        # Preprocess texts
        processed_texts = [preprocess_text(text) for text in texts]

        # Create and fit multilabel binarizer
        mlb = MultiLabelBinarizer()
        y = mlb.fit_transform(labels)

        # Create a pipeline with multiple classifiers
        # We'll train multiple models and choose the best one
        classifiers = {
            'logistic_regression': OneVsRestClassifier(LogisticRegression(solver='liblinear', max_iter=1000, C=1.0)),
            'random_forest': OneVsRestClassifier(RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)),
            'linear_svc': OneVsRestClassifier(LinearSVC(C=1.0, max_iter=1000, random_state=42))
        }

        # Create a TF-IDF vectorizer with n-grams
        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),  # Use both unigrams and bigrams
            min_df=2,            # Minimum document frequency
            max_df=0.9,          # Maximum document frequency
            sublinear_tf=True    # Apply sublinear tf scaling (log(tf))
        )

        # Transform the text data
        X = vectorizer.fit_transform(processed_texts)

        # Train all classifiers
        trained_classifiers = {}
        best_classifier = None
        best_score = 0

        for name, clf in classifiers.items():
            try:
                logger.info(f"Training classifier: {name}")
                clf.fit(X, y)

                # Simple evaluation on training data (in a real system, we would use cross-validation)
                score = clf.score(X, y)
                logger.info(f"Classifier {name} score: {score:.4f}")

                trained_classifiers[name] = clf

                # Keep track of the best classifier
                if score > best_score:
                    best_score = score
                    best_classifier = clf
            except Exception as e:
                logger.error(f"Error training classifier {name}: {str(e)}")

        # If no classifier worked, fall back to logistic regression
        if best_classifier is None:
            logger.warning("All classifiers failed, falling back to basic logistic regression")
            best_classifier = OneVsRestClassifier(LogisticRegression(solver='liblinear', max_iter=1000))
            best_classifier.fit(X, y)

        # Use the best classifier
        classifier = best_classifier
        logger.info(f"Using best classifier with score: {best_score:.4f}")

        # Save the model components
        with open(VECTORIZER_PATH, 'wb') as f:
            pickle.dump(vectorizer, f)

        with open(CLASSIFIER_PATH, 'wb') as f:
            pickle.dump(classifier, f)

        with open(BINARIZER_PATH, 'wb') as f:
            pickle.dump(mlb, f)

        logger.info("ML model trained and saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return False

def predict_ipc_sections(complaint_text):
    """
    Predict IPC sections for a given complaint text.

    Args:
        complaint_text: The text of the complaint

    Returns:
        A list of dictionaries with section codes and confidence scores
    """
    try:
        # Check if model exists
        if not (os.path.exists(VECTORIZER_PATH) and
                os.path.exists(CLASSIFIER_PATH) and
                os.path.exists(BINARIZER_PATH)):
            logger.warning("ML model not found. Training a new model...")
            train_model()

        # Load model components
        with open(VECTORIZER_PATH, 'rb') as f:
            vectorizer = pickle.load(f)

        with open(CLASSIFIER_PATH, 'rb') as f:
            classifier = pickle.load(f)

        with open(BINARIZER_PATH, 'rb') as f:
            mlb = pickle.load(f)

        # Preprocess and vectorize the text
        processed_text = preprocess_text(complaint_text)
        X = vectorizer.transform([processed_text])

        # Try to get prediction probabilities if available
        try:
            y_pred_proba = classifier.predict_proba(X)

            # Get the classes (IPC sections)
            classes = mlb.classes_

            # Create a list of (section, probability) tuples
            section_probs = [(section, prob) for section, prob in zip(classes, y_pred_proba[0])]
        except AttributeError:
            # If predict_proba is not available, use decision_function or predict
            logger.info("predict_proba not available, using alternative method")

            try:
                # Try decision_function first (for SVM models)
                y_pred_decision = classifier.decision_function(X)

                # Convert decision values to probabilities using sigmoid function
                import numpy as np
                def sigmoid(x):
                    return 1 / (1 + np.exp(-x))

                y_pred_proba_values = sigmoid(y_pred_decision[0])

                # Get the classes (IPC sections)
                classes = mlb.classes_

                # Create a list of (section, probability) tuples
                section_probs = [(section, prob) for section, prob in zip(classes, y_pred_proba_values)]
            except AttributeError:
                # If decision_function is not available, use predict
                logger.info("decision_function not available, using predict")

                y_pred = classifier.predict(X)

                # Get the classes (IPC sections)
                classes = mlb.classes_

                # Create a list of (section, probability) tuples with binary values
                section_probs = [(section, 0.85 if pred else 0.15) for section, pred in zip(classes, y_pred[0])]

        # Sort by probability (descending) and filter those with probability > 0.3 (increased threshold)
        section_probs = sorted([(s, p) for s, p in section_probs if p > 0.3], key=lambda x: x[1], reverse=True)

        # Limit to top 3 sections from ML model
        section_probs = section_probs[:3]

        # If ML model doesn't find good matches, fall back to keyword-based analysis
        if not section_probs:
            logger.info("ML model didn't find strong matches, using keyword analysis")
            keyword_results = keyword_based_analysis(complaint_text)

            # Convert the new format to the old format for compatibility
            section_probs = [(section, confidence) for section, confidence, _ in keyword_results]

            # Store matched keywords for later use
            matched_keywords_dict = {section: keywords for section, _, keywords in keyword_results}
        else:
            # For ML results, find matching keywords
            matched_keywords_dict = {}
            for section_code, _ in section_probs:
                matched_keywords_dict[section_code] = find_matching_keywords(complaint_text, section_code)

        # Convert to the expected format with better explanations
        results = []
        for section_code, confidence in section_probs:
            # Get section details from database
            section = LegalSection.query.filter_by(code=section_code).first()

            # Get matched keywords for this section
            keywords_matched = matched_keywords_dict.get(section_code, [])

            # Generate a more detailed explanation of relevance
            relevance_explanation = generate_relevance_explanation(complaint_text, section_code, confidence, keywords_matched)

            if section:
                results.append({
                    "section_code": section.code,
                    "section_name": section.name,
                    "section_description": section.description,
                    "confidence": float(confidence),
                    "relevance": relevance_explanation,
                    "keywords_matched": find_matching_keywords(complaint_text, section_code)
                })
            else:
                # If section not in database, provide basic info
                results.append({
                    "section_code": section_code,
                    "section_name": f"IPC Section {section_code}",
                    "section_description": "Description not available",
                    "confidence": float(confidence),
                    "relevance": relevance_explanation,
                    "keywords_matched": find_matching_keywords(complaint_text, section_code)
                })

        return results
    except Exception as e:
        logger.error(f"Error predicting IPC sections: {str(e)}")
        # Fall back to keyword-based analysis
        keyword_results = keyword_based_analysis(complaint_text)

        # Convert the new format to the old format for compatibility
        section_probs = [(section, confidence) for section, confidence, _ in keyword_results]

        # Store matched keywords for later use
        matched_keywords_dict = {section: keywords for section, _, keywords in keyword_results}

        results = []
        for section_code, confidence in section_probs:
            # Get section details from database
            section = LegalSection.query.filter_by(code=section_code).first()

            # Get matched keywords for this section
            keywords_matched = matched_keywords_dict.get(section_code, [])

            # Generate a more detailed explanation of relevance
            relevance_explanation = generate_relevance_explanation(complaint_text, section_code, confidence, keywords_matched)

            if section:
                results.append({
                    "section_code": section.code,
                    "section_name": section.name,
                    "section_description": section.description,
                    "confidence": float(confidence),
                    "relevance": relevance_explanation,
                    "keywords_matched": find_matching_keywords(complaint_text, section_code)
                })
            else:
                results.append({
                    "section_code": section_code,
                    "section_name": f"IPC Section {section_code}",
                    "section_description": "Description not available",
                    "confidence": float(confidence),
                    "relevance": relevance_explanation,
                    "keywords_matched": find_matching_keywords(complaint_text, section_code)
                })

        return results

def find_matching_keywords(text, section_code):
    """
    Find keywords in the text that match the given IPC section

    Args:
        text: The complaint text
        section_code: The IPC section code

    Returns:
        list: Matching keywords
    """
    if not text or section_code not in IPC_KEYWORDS:
        return []

    text = text.lower()
    matching_keywords = []

    for keyword in IPC_KEYWORDS.get(section_code, []):
        # Check for exact word match with word boundaries
        if re.search(r'\b' + re.escape(keyword) + r'\b', text):
            matching_keywords.append(keyword)

    return matching_keywords

def generate_relevance_explanation(text, section_code, confidence, matching_keywords=None):
    """
    Generate a detailed explanation of why a section is relevant to the complaint

    Args:
        text: The complaint text
        section_code: The IPC section code
        confidence: The confidence score
        matching_keywords: Optional list of matching keywords (if already computed)

    Returns:
        str: Explanation of relevance
    """
    # Get matching keywords if not provided
    if matching_keywords is None:
        matching_keywords = find_matching_keywords(text, section_code)

    # Get section information
    section = LegalSection.query.filter_by(code=section_code).first()
    section_name = section.name if section else f"Section {section_code}"

    # Generate explanation based on confidence level
    if confidence > 0.8:
        confidence_level = "very high"
    elif confidence > 0.6:
        confidence_level = "high"
    elif confidence > 0.4:
        confidence_level = "moderate"
    elif confidence > 0.2:
        confidence_level = "low"
    else:
        confidence_level = "very low"

    # Base explanation
    explanation = f"This complaint shows {confidence_level} relevance (score: {confidence:.2f}) to {section_name}."

    # Add keyword information if available
    if matching_keywords:
        if len(matching_keywords) == 1:
            explanation += f" The key term '{matching_keywords[0]}' was found in the complaint."
        else:
            keywords_str = ", ".join([f"'{k}'" for k in matching_keywords[:-1]]) + f" and '{matching_keywords[-1]}'"
            explanation += f" Key terms {keywords_str} were found in the complaint."

    # Add section-specific explanations
    if section_code == '302':
        explanation += " This section deals with murder and is applicable when there is death caused with the intention of causing death."
    elif section_code == '304A':
        explanation += " This section deals with death caused by negligence, not amounting to culpable homicide."
    elif section_code == '307':
        explanation += " This section applies to attempted murder cases where there was a clear intention to kill."
    elif section_code == '323' or section_code == '324':
        explanation += " This section applies to cases involving physical assault or causing hurt."
    elif section_code == '354':
        explanation += " This section applies to cases involving assault or criminal force against a woman with intent to outrage her modesty."
    elif section_code == '376':
        explanation += " This section applies to cases of rape or sexual assault."
    elif section_code == '379' or section_code == '380':
        explanation += " This section applies to cases of theft or stealing property."
    elif section_code == '392' or section_code == '395':
        explanation += " This section applies to robbery cases where theft involves force or threat."
    elif section_code == '406':
        explanation += " This section applies to criminal breach of trust cases where property entrusted is misappropriated."
    elif section_code == '420':
        explanation += " This section applies to cases of cheating and dishonestly inducing delivery of property."
    elif section_code == '498A':
        explanation += " This section applies to cases of cruelty by husband or relatives of husband against a woman."
    elif section_code == '504' or section_code == '506':
        explanation += " This section applies to cases involving intentional insult or criminal intimidation."

    return explanation

def analyze_complaint(complaint_text, language_code=None):
    """
    Analyze a complaint text and return relevant IPC sections.
    This is the main function to be called from other modules.

    Args:
        complaint_text: The text of the complaint
        language_code: Optional language code for non-English complaints

    Returns:
        A dictionary with sections and analysis
    """
    if not complaint_text:
        return {"sections": []}

    # Log the complaint for debugging
    logger.info(f"Analyzing complaint: {complaint_text[:100]}...")
    if language_code:
        logger.info(f"Language code: {language_code}")

    # Translate non-English text to English if needed
    translated_text = complaint_text
    original_language = None

    if language_code and language_code != 'en-US' and language_code != 'en-GB' and language_code != 'en-IN':
        try:
            # Try to use a translation service if available
            # For now, we'll just use the original text but log that translation would be needed
            logger.info(f"Translation would be needed for language: {language_code}")
            original_language = language_code
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")

    # Get IPC section predictions
    sections = predict_ipc_sections(translated_text)

    # Add information about original language if translated
    result = {
        "sections": sections
    }

    if original_language:
        result["original_language"] = original_language

    return result
