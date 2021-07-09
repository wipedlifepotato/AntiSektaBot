# -*- coding: utf-8 -*-
import config.config as config
import telebot, time
from telebot import types
from threading import Thread
import sqlite3
import os,sys
threads=[]

class BotThread(Thread):
    def __init__(self, bot):
        super(BotThread, self).__init__()
        self.bot=bot
    def run(self):
         self.bot.polling()

class AntiSektaHandler:
 def __init__(self, bot):
   self.bot=bot
   pass
 def GetLastVideo(self,  message, markup): pass
 def WelcomeMessage(self, message, markup): pass
 def HelpMessage(self, message, markup): pass
 def GetOurChannelMessage(self,  message, markup): pass
 def StartMessage(self, message, markup): 
  print("/start clicked by %s" % str(message.chat.id) )
  self.bot.reply_to(message, config.welcomeMessage % (config.BotName,message.from_user.first_name), reply_markup=markup)
  try:
   #self.bot.send_video(message.chat.id, "BAACAgIAAxkBAAJ3VV8IGQXKnjnXG5lUP166C4YOculoAAL_AgACFSAZScFu22y5ybGfGgQ")
   #time.sleep(2)
   self.bot.send_video(message.chat.id, "BAACAgIAAxkBAAKHDF-D8miTyn_sxrSf7rX_wlv1khcfAAL_AgACFSAZScFu22y5ybGfGwQ")
   #self.bot.send_message(message.chat.id,"" )
   conn = sqlite3.connect('channel.db')
   c = conn.cursor()
   #zzz=0
   for row in c.execute('SELECT DISTINCT * FROM ChannelPost ORDER BY messageid DESC LIMIT %d' % config.maxChannelPostInDB):
     #print(row)
    # zzz=zzz+1
     self.bot.forward_message(message.chat.id,row[0],row[1])
   #if zzz == 0:
     #  for row in self.bot.get_message(config.channelID, limit=config.maxChannelPostInDB):
      #  self.bot.forward_message(message.chat.id,row[0],row[1])
  except Exception as e:
   self.bot.reply_to(message, "some error?..."+str(e))
   pass
 def Rassylo4ka(self, bot): pass

def initBot(tok,row_width=config.width_keyboard):
 try:

  last_messages=[]
  notreply_messages=[]
  #dump_messages={}
  reply_get=0
  markup_all_commands = types.ReplyKeyboardMarkup(row_width=row_width)
  commands = ['/Связаться', '/Последнии_посты']

  for comm in commands:
   markup_all_commands.add(comm)
  bot=telebot.TeleBot(tok)
  AntiSekta = AntiSektaHandler(bot)

  print("Start bot '"+token+"' '"+str(bot)+"'")
  try:
   @bot.message_handler(commands=['getmyID','debuginfo'])
   def debug_handler(message):
    bot.reply_to(message, str(message) )


   @bot.message_handler(commands=['Помощь','help','help'])
   def help_handler(message):
    bot.reply_to(message, config.helpMessage % message.from_user.first_name, reply_markup=markup_all_commands)

   @bot.message_handler(commands=['Связаться','связь','админ'])
   def help_handler(message):
    bot.reply_to(message, config.ChannelURL, reply_markup=markup_all_commands)
    bot.reply_to(message, "Или напишите боту, он передаст администрации Ваше сообщение", reply_markup=markup_all_commands)

   @bot.message_handler(func=lambda m: True)
   def get_message(message):
        if int(message.from_user.id) in config.ownersID and "админка" in message.text: 
         markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
         if len(last_messages) == 0:
          bot.reply_to(message, 'нет новых сообщений', reply_markup=markup_all_commands)
          return True
         for m in last_messages:
          markup.add("Ответить на:"+m[1].text[:80])
         msg = bot.reply_to(message, 'ответить?', reply_markup=markup)
         bot.register_next_step_handler(msg, answers)
         #print(markup)
         return True
        #print( str(message) )
        #print( message.from_user.id , config.ownerID, int(message.from_user.id) == int(config.ownerID) )
        if message.reply_to_message != None and int(message.from_user.id) in config.ownersID:
          print("Message reply. ")
          if message.reply_to_message.forward_from == None:
           bot.send_message(message.reply_to_message.chat.id,
		 "Пользователь скрыл свой ID/Username, пишите ему через ID...")
          else:
           print( message.reply_to_message.forward_from )
           bot.send_message(message.reply_to_message.forward_from.id,"Администрация ответила вам на сообщение: ")
           bot.send_message(message.reply_to_message.forward_from.id, message.reply_to_message.text)
           bot.send_message(message.reply_to_message.forward_from.id,message.text)
           bot.send_message(message.reply_to_message.chat.id,
		 "Ваше сообщение было отправлено %s " % message.reply_to_message.forward_from.first_name)
          return True
        com=message.text.split(' ')
        if "/reply" in com[0] and len(com) > 2 and int(message.from_user.id) in config.ownersID:
          print("Reply! to %s msg %s" %(com[1], com[2:]) )
          tmpmsg=""
          for t in  com[2:]:
            tmpmsg=tmpmsg+" "+t
          bot.send_message(com[1],"Администрация ответила вам: ")
          bot.send_message(com[1], tmpmsg)
          bot.send_message(message.chat.id, "Ваше сообщение было пересланно на ID %s" % com[1])
          return True
        if "/start" in com[0]:  
          AntiSekta.StartMessage(message, markup_all_commands)
          pass
        elif "/Рассылка" in com[0] or "/Последнии_посты" in com[0]:
         try:
          conn = sqlite3.connect('channel.db')
          c = conn.cursor()
          for row in c.execute('SELECT DISTINCT * FROM ChannelPost ORDER BY messageid DESC LIMIT %d' % config.maxChannelPostInDB):
           bot.forward_message(message.chat.id,row[0],row[1])
         except Exception as e:
          bot.reply_to(message, "some error?..."+str(e))
          pass 
        else: #int(message.from_user.id) not in config.ownersID:
         ndtime=0
         floodcount=0
         if int(message.from_user.id) not in config.ownersID:
          for m in last_messages:
           if message.chat.id in m:
             floodcount=m[3]+1
             if floodcount>5:
              wmsg="WARNING[%s]: какой-то чел флудит боту %s\n" % (time.strftime("%c"), str(message))
              print("WARNING: FLOOD DETECTED!! FROM CHATID(more info in FLOODLIST %s" % str(message.chat.id) )
              f=open("FLOODLIST.txt", "a")
              f.write(wmsg)
              f.close()
             if time.time() - m[2] > config.delaymessage: 
              last_messages.remove(m)
              floodcount=0
              break
             else: 
              last_messages.remove(m)
              last_messages.append( (message.chat.id, message, time.time(),floodcount ) )
              ndtime=config.delaymessage - int((time.time() - m[2]))+1
              #notreply_messages=last_messages
             bot.reply_to( message, 'Подождите некоторое время перед отправой сообщения (~%d секунд)' % ndtime )
             return False
         #print( str(message) ) 
         #dump_messages[message.message_id]=message
         last_messages.append( (message.chat.id, message, time.time(), floodcount) )
         for owner in config.ownersID:
          try:
           bot.forward_message(owner,message.chat.id,message.message_id)
           bot.send_message(owner, "/reply %d Ваше сообщение что бы ответить тому кто это написал" % (message.chat.id) )
           notreply_messages.append( (message.text, message) )
          except Exception as exc:
           print( "OWner id %d not found" % owner )
         bot.reply_to(message, 'Ваше сообщение: "%s" было передано владельцу бота' % message.text)
        #else: bot.send_message(message.chat.id, "Вы хотите послать сообщение сами себе?")
   @bot.message_handler(commands=['/start'])
   def welcome_handler(message): # 
    AntiSekta.StartMessage(message,markup_all_commands)
    print("/start clicked by %s" % str(message.chat.id) )
 
   def final_answer(message):
    global reply_get, reply_get_message
    if reply_get != 0:
     bot.send_message(reply_get, "Вам пришёл ответ на сообщение: %s :" % reply_get_message)
     bot.send_message(reply_get, message.text)
     bot.reply_to(message, "Ваше сообщение было отправленно получателю с ID %d вы можете так же писать ему через команду /reply ID сообщение" % reply_get, reply_markup=markup_all_commands )
     reply_get=0
     reply_get_message=""
   def answers(message): #отвечать человекам
    chat_id=message.chat.id
    text=message.text
    print( chat_id, text )

    for reply in notreply_messages:
     for r in reply:
      if str(r) in message.text:
       print ( str(r), "in", message.text)
       global reply_get, reply_get_message
       reply_get=reply[1].chat.id
       reply_get_message=reply[0]
       bot.reply_to(message,"введите ваш ответ на сообщение '%s'" % reply[0])
       bot.register_next_step_handler(message, final_answer)
       print("Registered")
       notreply_messages.remove(reply)
       print("removed")
       return True

     
   @bot.channel_post_handler(content_types=["text", "sticker", "pinned_message", "photo", "audio", "video", "voice"])
   @bot.channel_post_handler(func=lambda m: True)
   def handle_channel_post(post):
    if post.chat.id != config.channelID:
     print("WARNING: some channel %d want use it bot" % post.chat.id)
     return False
    try:
     conn = sqlite3.connect('channel.db')
     c = conn.cursor()
     #for owner in config.ownersID:
     #for count in c.execute('SELECT COUNT(*) FROM ChannelPost'):
      #if count[0] > config.maxChannelPostInDB*2:
       #c.execute('DELETE FROM ChannelPost')
     c.execute("INSERT INTO ChannelPost VALUES('%s', '%s')" % (post.chat.id, post.message_id))
     conn.commit()
     conn.close()
     print("Added last post")
          #bot.forward_message(1111061266,post.chat.id,post.message_id)
     #bot.forward_message(config.ownerID,message.chat.id,message.message_id)
     #print(post)
    except Exception as exc:
      print( str(exc) )
   @bot.message_handler(content_types=['document', "sticker", "pinned_message", "photo", "audio"])
   def handle_files_stickers(message):
     try:
         for owner in config.ownersID:
          bot.forward_message(owner,message.chat.id,message.message_id)
         bot.reply_to(message, 'Ваш файл был отправлен владельцам бота')
     except Exception as exc:
      print( str(exc) )
  except Exception as exc:
    print( str(exc) )
 except Exception as exc:
    print( str(exc) )
 thread=BotThread(bot)
 threads.append(thread)
 thread.start()
 print("thread inited")

while True:
 for token in config.tokens:
  initBot(token)
 for thread in threads:
  thread.join()
#  os.system("python3 ./"+sys.argv[0]) 
#  sys.exit()

