"""
Additional training cases for the IPC section prediction model.
Contains a mix of short and long descriptions for various IPC sections.
"""

# New training cases to be added to the model
NEW_TRAINING_CASES = [
    # Short descriptions (10 cases)
    ("The accused stole my mobile phone at the bus station.", ["379"]),
    ("My neighbor threatened to kill me if I complained about the noise.", ["506"]),
    ("The accused forged my signature on a loan document.", ["465", "468"]),
    ("The accused slapped me during an argument.", ["323"]),
    ("My wallet was pickpocketed at the market.", ["379"]),
    ("The accused broke into my house at night.", ["457"]),
    ("The accused sent me obscene messages online.", ["509", "67A"]),
    ("The accused cheated me by selling a fake gold necklace.", ["420"]),
    ("The accused hit me with a cricket bat.", ["324"]),
    ("My car was damaged by the accused.", ["427"]),
    
    # Long descriptions (15 cases)
    ("""On the evening of 15th June 2023, at approximately 8:30 PM, I was walking home from work through City Park when I was approached by the accused. He demanded that I hand over my wallet and mobile phone. When I hesitated, he pulled out a knife and threatened to stab me if I didn't comply. Fearing for my life, I handed over my belongings worth approximately Rs. 25,000. The accused then fled the scene. I immediately reported the incident to the nearest police station.""", ["392", "397"]),
    
    ("""I had given Rs. 5,00,000 to the accused on 10th January 2023 for investment in his company, which he claimed would give me 20% returns within 6 months. He provided me with fake investment certificates and company documents. After 6 months, when I asked for my money back, he made excuses and eventually stopped responding to my calls. I later discovered that several others had been similarly defrauded by him, and that the company did not actually exist.""", ["420", "406"]),
    
    ("""The accused, who is my husband, has been subjecting me to physical and mental cruelty for the past two years due to dowry demands. On multiple occasions, he has beaten me, leaving visible bruises. His family members, particularly his mother and brother, have been constantly harassing me for not bringing enough dowry. They have been demanding an additional Rs. 10,00,000 and a car. On 5th July 2023, after I refused to ask my parents for more money, my husband assaulted me severely, resulting in a fractured arm.""", ["498A", "323", "325"]),
    
    ("""On 20th March 2023, I discovered that the accused had been stalking me for several weeks. He would follow me to my workplace, wait outside my residence, and send me numerous unwanted messages despite my clear refusal. On the mentioned date, he followed me to a restaurant where I was having dinner with friends, approached our table, and created a scene by shouting and threatening me. He also made several obscene gestures and comments, causing me significant distress and humiliation in public.""", ["354D", "509"]),
    
    ("""I am the owner of a shop in the local market. On the night of 7th August 2023, at around 2:00 AM, a group of five individuals broke into my shop by breaking the lock. They stole merchandise worth approximately Rs. 3,00,000, including electronic items, cash, and other valuables. The entire incident was captured on the CCTV camera installed in my shop. I can identify at least three of the accused persons from the footage.""", ["395", "457"]),
    
    ("""The accused, who is my business partner, has misappropriated company funds amounting to Rs. 15,00,000. We started the business together in January 2022, with equal investments. In June 2023, I discovered through our accountant that the accused had been transferring company money to his personal account without my knowledge or consent. When confronted, he admitted to using the funds for personal expenses but refused to return the money or provide any explanation.""", ["406", "408"]),
    
    ("""On 12th September 2023, while I was driving on the highway, the accused, who was driving a truck, hit my car from behind at high speed. The impact caused my car to veer off the road and hit a tree. I sustained multiple injuries including a broken leg and several lacerations. Medical reports confirm that the accused was driving under the influence of alcohol at the time of the accident. The damage to my vehicle is estimated at Rs. 2,50,000.""", ["279", "337", "338"]),
    
    ("""The accused, who is my tenant, has refused to vacate my property despite the expiration of the lease agreement on 31st May 2023. I served him a legal notice on 1st June 2023, giving him 30 days to vacate. However, he has not only refused to leave but has also stopped paying rent since April 2023. When I visited the property on 5th July 2023 to discuss the matter, he threatened me with violence if I tried to evict him.""", ["441", "506"]),
    
    ("""I had employed the accused as a domestic helper in my house. On 25th October 2023, I discovered that she had been stealing valuable items from my home over a period of several months. Items missing include gold jewelry worth approximately Rs. 2,00,000, cash amounting to Rs. 50,000, and several electronic gadgets. When confronted with evidence from the hidden camera I had installed, she admitted to the theft but refused to return the stolen items.""", ["381"]),
    
    ("""On 3rd November 2023, I received an email from the accused claiming to be from my bank. The email stated that my account had been compromised and I needed to verify my details by clicking on a link and entering my account information. Believing it to be genuine, I followed the instructions. The next day, I discovered that Rs. 1,50,000 had been transferred from my account without my authorization. Upon investigation, it was revealed that the email was fraudulent and part of a phishing scam operated by the accused.""", ["420", "66C", "66D"]),
    
    ("""The accused, who is my colleague, has been spreading false rumors about me in our workplace since August 2023. He has been telling our coworkers and superiors that I am involved in embezzlement of company funds and that I secured my position through improper means. These allegations are completely false and have severely damaged my reputation and standing in the company. As a result, I was passed over for a promotion that I was qualified for.""", ["499", "500"]),
    
    ("""On 15th December 2023, I was attending a public gathering when the accused, who is a local political leader, delivered a speech inciting violence against my religious community. He made several derogatory remarks about our religious practices and called upon the crowd to boycott businesses owned by members of our community. His speech led to a mob forming, which later vandalized several shops owned by people from my community, including my own store.""", ["153A", "295A"]),
    
    ("""I am a government official working in the Revenue Department. On 10th January 2024, the accused offered me a bribe of Rs. 50,000 to manipulate land records in his favor. When I refused and warned him that I would report the matter, he threatened to harm my family if I did not comply with his demands. He specifically mentioned details about my children's school and daily routine, which caused me significant fear and distress.""", ["171B", "506"]),
    
    ("""The accused, who is my ex-spouse, abducted our minor child (aged 5 years) from school on 20th February 2024 without my knowledge or consent, despite the court granting me full custody after our divorce. He took our child to an unknown location and has been refusing to disclose their whereabouts. He has been sending me threatening messages, demanding that I withdraw the property case against him in exchange for information about our child.""", ["363", "365", "506"]),
    
    ("""On 5th March 2024, I discovered that the accused had created a fake social media profile using my name and photographs. Through this profile, he had been posting objectionable content and making inappropriate comments to my friends and colleagues. He also shared morphed images of me in compromising positions. This has caused me severe emotional distress and damaged my reputation among my social and professional circles.""", ["499", "500", "67A"]),
]
