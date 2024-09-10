import os
import json
def extractConfig(nameModel="SystemData",relPath=os.path.join("private/experiment_config.json"),dataOut="keygroq"):
    configPath=os.path.join(os.getcwd(),relPath)
    with open(configPath, 'r', encoding='utf-8') as file:
        config = json.load(file)[nameModel]
    Output= config[dataOut]
    return Output

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


def AnalysisContract(source):
    keygroq=extractConfig(nameModel="SystemData",dataOut="keygroq")
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
        model="llama-3.1-70b-versatile",
    )
    return chat_completion.choices[0].message.content
