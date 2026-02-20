async def textFunctionGemini(message, guildMap):
    guildID = str(message.guild.id)                    #shorthand
    geminiOBJ = guildMap[guildID]["geminiOBJ"]                 #shorthand

    geminiOBJ.geminiReset(False)
    messageContant = message.content
    temp = geminiOBJ.preprocessor(messageContant)
    # [bool (ratelimited if true), bool (send to ai if true), str]
    if temp [0] == True:
        return ""
    
    if temp[1] == True:
        #this need to return the response, do not send it    
        return await geminiOBJ.processing(message,temp[2], message.attachments[0] if message.attachments else None)
    return temp[2]
