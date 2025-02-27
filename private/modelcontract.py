import os
import json

prompt="""You are an expert in blockchain smart contract analysis. You will be provided with the source code of a smart contract. Your task is to perform a comprehensive analysis of the contract, covering the following aspects:

Functionality Analysis:

- Identify and explain the main functions of the contract.
- Describe the general purpose of the contract.
- Analyze how different parts of the code interact.

Sector and Use Classification:

Determine in which funtions used. The funtions you can mention are only [DeFi, NFTs, Governance, Play-to-Earn Games,Prediction Markets,Reward Systems in Content Platforms, Fungible Tokens, Real Asset Tokenization Systems, Self-Sovereign Identity Systems, Credential Verification, Decentralized Reputation Management]

Identification of Potential Issues:

- Review the code for common security vulnerabilities in smart contracts.
- Identify possible inefficiencies in gas usage.
- Point out areas where the code could be improved in terms of clarity or optimization.
- Warn about any practices that could lead to scalability or maintenance issues.

Summary and Recommendations:

- Provide a concise summary of key findings.
- Offer recommendations for improving the contract.

Format a json:

{"Functionality Analysis":[Your detailed analysis here], "Sector and Use Classification":[Your classification and without explanation here],"Identification of Potential Issues":[Your list of potential problems here],"Summary and Recommendations":[Your summary and recommendations here]}


Ensure that your analysis is detailed yet concise, using appropriate technical terminology for smart contracts and blockchain development. If you find anything unusual or innovative in the code, make sure to mention it.

Smart Contract Code to analyze:

%s

Please proceed with your analysis based on the provided code.
Respond only with valid JSON. Do not write an introduction or summary.

"""    


def AnalysisContract(keygroq,source):
    """
    Contacts Groq API to complete a message based on a given source.

    Args:
        keygroq (str): The API key used to authenticate the Groq client.
                source (str): The source to be used in the chat completion prompt.
                
    Returns:
        str: The completed message content, specifically the first choice from the chat completion.
        - This content is based on the source provided and the Groq model "llama-3.3-70b-versatile" used for the completion.
                        
    Raises:
        Exception: If there's an issue with the API key, the Groq client, or the chat completion request, an exception may be raised.
        - This can happen if the API key is invalid, if there's a network issue, or if the Groq service is unavailable."""    
    from groq import Groq
    client = Groq(
    api_key=keygroq,
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt%(source),
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content
"""
Contacts Groq API to complete a message based on a given source.

Args:
    keygroq (str): The API key used to authenticate the Groq client.
            source (str): The source to be used in the chat completion prompt.
            
Returns:
    str: The completed message content, specifically the first choice from the chat completion.
                    - This content is based on the source provided and the Groq model "llama-3.3-70b-versatile" used for the completion.
                    
                    Raises:
                            Exception: If there's an issue with the API key, the Groq client, or the chat completion request, an exception may be raised.
                                          - This can happen if the API key is invalid, if there's a network issue, or if the Groq service is unavailable."""