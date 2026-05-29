from langchain_core.prompts import ChatPromptTemplate

########################
### zero-shot prompt ###
########################
prompt_zs = ChatPromptTemplate.from_template("""
You are a network engineer extracting BGP community values and their corresponding descriptions.
For communities with a placeholder (e.g., 'x', 'peer', 'asn'), find the meaning of the placeholder in the surrounding text and unfold the placeholder correspondingly.
Do not hallucinate values that are not present. For bgp community meaning that is not English, translate to English.

<<<BEGIN DOCUMENT>>>
{chunk}
<<<END DOCUMENT>>>
""")

########################
### few-shot cot prompt ###
########################
prompt_fs = ChatPromptTemplate.from_template("""
You are a network engineer extracting BGP community values and their corresponding descriptions.
For communities with a placeholder (e.g., 'x', 'peer', 'asn'), find the meaning of the placeholder in the surrounding text and unfold the placeholder correspondingly.
Do not hallucinate values that are not present. For bgp community meaning that is not English, translate to English.

For example:
60764:151x - AS57304 RETN

Where "x" means:
x = 0 : Do Not Advertise to peer
X = 1 : Prepend once
X = 9 : Advertise unconditionally

Let's think step by step.
- The words "Do not advertise" comes before it → it's likely the intended meaning. 
- "60764:151x" matches the format of bgp community value with a placeholder x → extract it.
- x is a placeholder with 3 values [0,1,9], each has its own meaning → extract all values with corresponding meaning.

Output: 
[{{'bgp_community': '60764:1510','description': 'do not advertise to peer AS57304 RETN'}},
{{'bgp_community': '60764:1511",'description': 'prepend one time when advertise to peer AS57304 RETN'}},
{{'bgp_community': '60764:1519",'description': 'advertise unconditionally to peer AS57304 RETN'}}]
                                          
<<<BEGIN DOCUMENT>>>
{chunk}
<<<END DOCUMENT>>>
""")
