import time
from datetime import date
from typing import Any
from telegram import Update, Message, Bot, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import json
import asyncio

dont_start_with_hash = list()
starts_with_hash = list()
number_of_occurrences = dict()
# number_of_occurrences.setdefault(Any,0)


async def wait(bot,chat_id,message_id,message_text):
    try:
        await bot.edit_message_text(chat_id=chat_id,message_id=message_id,text="#" + message_text.replace(' ','_'))
    except:
        try:
            await bot.edit_message_caption(chat_id=chat_id,message_id=message_id,caption="#" + message_text.replace(' ','_'))
        except:
            time.sleep(1)
            print("loading...")
            await wait(bot,chat_id,message_id,message_text)

async def editMessages(update = Update, context = ContextTypes.DEFAULT_TYPE) -> None:
    
    with open('chatExport.json','rt',encoding='utf-8') as f: 
        ff = f.read()
    chat_export = json.loads(ff)
    
    chat_id = update.channel_post.chat_id
    chat_type = chat_export['type']
    bot = update.channel_post.get_bot()
    await bot.delete_message(chat_id,update.channel_post.message_id)
    
    for d in chat_export['messages']:
        
        message_id = d['id']
        message_type = d['type']
        message_text_entities = d['text_entities']
        
        if message_type != 'message':
            continue
        
        next = False
        for k in d.keys():
            if k == 'forwarded_from':
                next = True
        
        if next:
            print(f"Skipped forwarded {message_id}")
            continue
        
        if d['text'] == "":
            continue
        
        message_text = message_text_entities[0]['text']
        if message_text.startswith('#Agradecimiento') or message_text.startswith('#promo'):
            print(f"Skipped {message_text}")
            continue
        
        print(f"Analyzing : [ {message_id} ] : {message_text}")
        
        if not message_text.startswith('#'):   #si no empieza con #
            
            print(f'Editing : [ {message_id} ] : {message_text}')
            
            try:
                await bot.edit_message_caption(chat_id=chat_id,message_id=message_id,caption="#" + message_text.replace(' ','_'))
            except:
                
                try:
                    await bot.edit_message_text(chat_id=chat_id,message_id=message_id,text= "#" + message_text.replace(' ','_') )
                except:
                    print(f"Failed at {message_id}\nWaiting for retry...")
                    await wait(bot,chat_id,message_id,message_text)
                    
            print("Successfully edited")
    print("Done")

async def restart(update:Update, context: list) -> None:
    dont_start_with_hash.clear()
    await update.message.reply_text("Done")
    
async def getIndex(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open('chatExport.json','rt',encoding='utf-8') as f: 
        ff = f.read()
    chat_export = json.loads(ff)
    for d in chat_export['messages']:
        message_id = d['id']
        message_type = d['type']
        message_text_entities = d['text_entities']
        
        if message_type != 'message':
            continue
        
        next = False
        for k in d.keys():
            if k == 'forwarded_from':
                next = True
        
        if next or d['text'] == "":
            print(f"Skipped forwarded {message_id}")
            continue
        
        message_text = message_text_entities[0]['text']
        mk = False
        for param in context.args:
            # print(param)
            if message_text.lower() == ("#" + param.lower()):
                mk = True
        if mk or message_text.startswith("# ") or message_text.startswith("#👀") or message_text.startswith('#Agradecimiento') or message_text.startswith('#promo'):
            print(f"Skipped {message_text}")
            mk = False
            continue
        
        # for i in number_of_occurrences.keys():
        #     if i == message_text:
        #         number_of_occurrences[message_text] += 1
        #         found = True
        #         break
        if number_of_occurrences.get(message_text.casefold(),-1) == -1:
            number_of_occurrences[message_text.casefold()] = 1
        else:
            number_of_occurrences[message_text.casefold()] += 1
            
    index_list = list()
    for i in number_of_occurrences:
        index_list.append(f" ~ {i} : {number_of_occurrences[i]}\n")
    index_list.sort()
    index = f"#Index\nACTUALIZADO [ {date.today()} ]\n"
    for i in range(len(index_list)):
        index += index_list[i]
    await update.message.reply_text(index)
    number_of_occurrences.clear()
        
def main() -> None:
    
    app = ApplicationBuilder().token("6271457988:AAHDMJc2lrmVJJzgSOsA413J35ImN_yPdQk").connect_timeout(30.0).pool_timeout(30.0).read_timeout(30.0).build()
    print("Bot running")

    # app.add_handler(CommandHandler("edit", editMessages, filters= filters.ChatType.CHANNEL))
    app.add_handler(CommandHandler("get_index", getIndex))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
        
