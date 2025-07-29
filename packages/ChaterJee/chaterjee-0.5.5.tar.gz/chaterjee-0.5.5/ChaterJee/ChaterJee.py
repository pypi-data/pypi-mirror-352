import os, sys
import time
from datetime import datetime
import urllib.parse
import asyncio
import pickle
import html
import traceback
import logging, json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters, PollAnswerHandler, PollHandler
from telegram.constants import ParseMode
import os.path
import threading
import subprocess
from subprocess import PIPE, Popen
from pathlib import Path

start_txt = \
"""
I am ChaterJee, a Research assistant Bot developed by Pallab Dutta in 2025.

*TEXT*
acts as a bash command and runs on host terminal.

*COMMANDS*
/start : returns this text.
/jobs : shows your jobs
/clear : clears chat history
/edit file.json : let you edit the file.json

"""

class ChatLogs:
    def __init__(self, TOKEN, CHATID):
        self.home = Path.home()
        self.TOKEN = TOKEN
        self.CHATID = CHATID
        self.txt = ''
        self.fig = ''
        self.path = os.popen('pwd').read()[:-1]
        self.smsID = []
        self.dict = {}
        self.jobs = {}
        self.runexe = "run.sh"
        self.killexe = "kill_run.sh"

    def cmdTRIGGER(self, read_timeout=7, get_updates_read_timeout=42):
        #que = asyncio.Queue()
        application = ApplicationBuilder().token(self.TOKEN).read_timeout(read_timeout)\
                .get_updates_read_timeout(get_updates_read_timeout).build()
        #updater = Updater(application.bot, update_queue=que)

        start_handler = CommandHandler('start', self.start)
        application.add_handler(start_handler)

        jobrun_handler = CommandHandler('run', self.runjob)
        application.add_handler(jobrun_handler)

        #fEdit_handler = CommandHandler('edit', self.EditorBabu)
        #application.add_handler(fEdit_handler)

        #cmd_handler = CommandHandler('sh', self.commands)
        #application.add_handler(cmd_handler)

        #cancel_handler = CommandHandler('cancel', self.cancel)
        #application.add_handler(cancel_handler)

        jobs_handler = ConversationHandler(\
        entry_points=[CommandHandler("jobs", self.ShowJobs),\
                    CommandHandler("clear", self.ask2clear),\
                    CommandHandler("edit", self.EditorBabu),\
                    CommandHandler("kill", self.ask2kill)],\
        states={
            0: [MessageHandler(filters.Regex("^(JOB)"), self.StatJobs)],
            1: [MessageHandler(filters.Regex("^(Yes|No)$"), self.ClearChat)],
            2: [MessageHandler(filters.Regex("^(FILE)"), self.SendEditButton)],
            3: [MessageHandler(filters.Regex("^(Yes|No)$"), self.killjob)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        application.add_handler(jobs_handler)

        application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.web_app_data))
        application.add_handler(MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^(JOB:|FILE:|Yes$|No$)")), self.commands))

        #await application.shutdown()
        #await application.initialize()

        #updater = Updater(application.bot, update_queue=que)
        #await updater.initialize()
        #await updater.start_polling()
        application.run_polling()

    async def sendUpdate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(self.txt):
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            msg = await context.bot.send_message(chat_id=self.CHATID, text=self.txt, parse_mode='Markdown')
            self.smsID.append(msg.message_id)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        self.txt = start_txt
        await self.sendUpdate(update, context)

    def register_to_log(self, job_name: str, log_path: str):
        self.jobs[job_name] = log_path

    async def ShowJobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        self.smsID.append(update.message.message_id)
        jobs_file = self.home / ".data" / "JOB_status.json"
        with open(jobs_file, 'r') as ffr:
            jobs = json.load(ffr)
        self.jobs = jobs

        reply_keyboard = [[f'{job}'] for job in list(self.jobs.keys())[::-1]]   # inverse to show latest jobs on top
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text("Select a job to get updates on",\
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Select the job."\
        ),\
        )
        self.smsID.append(msg.message_id)
        return 0

    async def StatJobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        job_name = update.message.text
        
        jobs_file = self.home / ".data" / "JOB_status.json"
        with open(jobs_file, 'r') as ffr:
            jobs = json.load(ffr)
        self.jobs = jobs

        logDIR = Path(jobs[job_name]['logDIR'])
        logFILE = jobs[job_name]['logFILE']
        logIMAGE = jobs[job_name]['logIMAGE']
        logDICT = jobs[job_name]['logDICT']
        
        self.txt = self.get_last_line(logDIR / logFILE)

        if self.txt is None:
            self.txt = 'No updates found'
            #await self.sendUpdate(update, context)
            #msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
            #self.smsID.append(msg.message_id)
        elif logDICT is not None:
            self.txt = self.txt + '\n'
            for key, value in logDICT.items():
                self.txt = self.txt + f"{key}: {value}\n"
        
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text(
            self.txt, reply_markup=ReplyKeyboardRemove()
        )
        self.smsID.append(msg.message_id)

        try:
            with open(logDIR / logIMAGE, 'rb') as ffrb:
                await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
                msg = await context.bot.send_photo(chat_id=self.CHATID, photo=ffrb)
                self.smsID.append(msg.message_id)
        except:
            pass

        return ConversationHandler.END

    def get_last_line0(self, filepath):
        with open(filepath, 'rb') as f:
            # Go to the end of file
            f.seek(0, 2)
            end = f.tell()

            # Step backwards looking for newline
            pos = end - 1
            while pos >= 0:
                f.seek(pos)
                char = f.read(1)
                if char == b'\n' and pos != end - 1:
                    break
                pos -= 1

            # Read from found position to end
            f.seek(pos + 1)
            last_line = f.read().decode('utf-8')
            return last_line.strip()

    def get_last_line(self, filepath):
        if not os.path.exists(filepath):
            return None

        try:
            command_chain = f"tail -n 1000 '{filepath}' | grep -Ev '^\s*$' | tail -n 1"
            process = subprocess.run(command_chain, shell=True, capture_output=True, text=True, check=True)
            
            output = process.stdout.strip()
            if output:
                return output
            else:
                return None

        except subprocess.CalledProcessError as e:
            return None
        except FileNotFoundError:
            return None
        except Exception as e:
            return None

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text(
        "Keyboard is refreshed!", reply_markup=ReplyKeyboardRemove()
        )
        self.smsID.append(msg.message_id)
        return ConversationHandler.END

    async def EditorBabu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        if len(context.args) == 1:
            file_path = context.args[0]
            if os.path.exists(file_path):
                with open(file_path,'r') as ffr:
                    JsonStr = json.load(ffr)
                encoded_params = urllib.parse.quote(json.dumps(JsonStr))
                file_name = file_path.split('/')[-1]
                extender = f"?variables={encoded_params}&fileNAME={file_name}"
                await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
                msg = await update.message.reply_text(
                    "Editor-Babu is opening the Json file.",
                    reply_markup=ReplyKeyboardMarkup.from_button(
                        KeyboardButton(
                            text="Editor Babu",
                            web_app=WebAppInfo(url="https://pallab-dutta.github.io/EditorBabu"+extender),
                        )
                    ),
                )
                self.smsID.append(msg.message_id)
            else:
                self.txt = f"File {file_path} not Found!"
                await self.sendUpdate(update, context)
            return ConversationHandler.END
        else:
            JSONfiles = self.get_json_files(".")
            #self.txt = "Expected a JSON file as argument. Nothing provided."
            #await self.sendUpdate(update, context)
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            if len(JSONfiles):
                msg = await update.message.reply_text("Select a JSON file to edit",\
                    reply_markup=ReplyKeyboardMarkup(JSONfiles, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Select the file."\
                    ),\
                    )
                self.smsID.append(msg.message_id)
                return 2
            else:
                self.txt = f"No JSON file found in the current directory!"
                await self.sendUpdate(update, context)
                return ConversationHandler.END

    def get_json_files(self, directory):
        json_files = []
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                json_files.append([f"FILE: {filename}"])
        return json_files

    async def SendEditButton(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        #print("I'm here!")
        self.smsID.append(update.message.message_id)
        file_name = update.message.text[6:]
        #print(file_name)
        with open(file_name,'r') as ffr:
            JsonStr = json.load(ffr)
            encoded_params = urllib.parse.quote(json.dumps(JsonStr))
        extender = f"?variables={encoded_params}&fileNAME={file_name}"
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text(
            "Editor-Babu is opening the Json file.",
            reply_markup=ReplyKeyboardMarkup.from_button(
                KeyboardButton(
                    text="Editor Babu",
                    web_app=WebAppInfo(url="https://pallab-dutta.github.io/EditorBabu"+extender),
                    ),
                resize_keyboard=True, one_time_keyboard=True
                ),
            )
        self.smsID.append(msg.message_id)
        return ConversationHandler.END

    async def web_app_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None :
        self.smsID.append(update.message.message_id)
        data = json.loads(update.effective_message.web_app_data.data)
        formname = data['formNAME']
        if formname == 'EditorBabu':
            fileNAME = data['fileNAME']
            del data['formNAME']
            del data['fileNAME']
            if len(data):
                with open(fileNAME, 'r') as ffr:
                    JSdata = json.load(ffr)
                JSdata = {**JSdata, **data}
                with open(fileNAME, 'w') as ffw:
                    json.dump(JSdata, ffw, indent=4)
                #await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
                #msg = await update.message.reply_text(
                #    f"edits are saved to {fileNAME}", reply_markup=ReplyKeyboardRemove()
                #)
                #self.smsID.append(msg.message_id)
                self.txt = f"edits are saved to {fileNAME}"
            else:
                #await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
                #msg = await update.message.reply_text(
                #    f"No new changes! file kept unchanged.", reply_markup=ReplyKeyboardRemove()
                #)
                #self.smsID.append(msg.message_id)
                self.txt = f"No new changes! file kept unchanged."
            await self.sendUpdate(update, context)
            #return ConversationHandler.END

        #msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
        #self.smsID.append(msg.message_id)
        #await self.sendUpdate(update, context)

    async def commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        #cmd2run = ' '.join(context.args) #update.message.text.strip()
        cmd2run = update.message.text.strip()
        cmd0 = cmd2run.split(' ')[0]
        if cmd0[0]=='/':
            print('It came here')
            pass
        elif cmd0=='cd':
            cmd1 = cmd2run[3:]
            try:
                os.chdir(cmd1)
                self.txt=os.popen('pwd').read()
            except:
                self.txt='path not found'
        elif cmd0=='clear':
            self.txt="This clears the terminal screen!\nTo clear telegram screen type /clear"
        elif cmd0=='pkill':
            self.txt="pkill cannot be called."
        else:
            print('command: ',cmd2run)
            cmd=cmd2run
            try:
                self.txt=os.popen('%s'%(cmd)).read()
            except:
                self.txt='error !'
        await self.sendUpdate(update, context)
        #msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
        #self.smsID.append(msg.message_id)

    async def ClearChat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        if update.message.text == 'Yes':
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            msg = await update.message.reply_text(
            "Full chat history will be cleared", reply_markup=ReplyKeyboardRemove()
            )
            self.smsID.append(msg.message_id)
            for i in self.smsID:
                try:
                    await context.bot.delete_message(chat_id=self.CHATID, message_id=i)
                except:
                    pass
            
            self.smsID = []
            return ConversationHandler.END
        elif update.message.text == 'No':
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            msg = await update.message.reply_text(
            "Chat history is kept uncleared", reply_markup=ReplyKeyboardRemove()
            )
            self.smsID.append(msg.message_id)
            return ConversationHandler.END

    async def ask2clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        self.smsID.append(update.message.message_id)
        reply_keyboard = [['Yes','No']]
        print(reply_keyboard)
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text("Entire chat history in the current session will be cleared. Proceed?",\
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Select to proceed."\
        ),\
        )
        self.smsID.append(msg.message_id)
        return 1

    async def runjob(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        cmd = f"./{self.runexe}"
        try:
            os.popen('%s'%(cmd))#.read()
            self.txt='job submitted !'
        except:
            self.txt='error !'
        await self.sendUpdate(update, context)

    async def ask2kill(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        self.smsID.append(update.message.message_id)
        reply_keyboard = [['Yes','No']]
        print(reply_keyboard)
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text("Your job will be killed. Proceed?",\
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Select to proceed."\
        ),\
        )
        self.smsID.append(msg.message_id)
        return 3

    async def killjob(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        cmd = f"./{self.killexe}"
        try:
            txt = os.popen('%s'%(cmd)).read()
        except:
            txt='error !'

        self.smsID.append(update.message.message_id)
        if update.message.text == 'Yes':
            txt = os.popen('%s'%(cmd)).read()
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            msg = await update.message.reply_text(
            txt, reply_markup=ReplyKeyboardRemove()
            )
        elif update.message.text == 'No':
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            msg = await update.message.reply_text(
            "Your job is not killed.", reply_markup=ReplyKeyboardRemove()
            )
        self.smsID.append(msg.message_id)
        return ConversationHandler.END


class NoteLogs:
    def __init__(self):
        self.home = Path.home()
        self.jobNAME = None
        self.logDIR = None
        self.logFILE = None
        self.logIMAGE = None
        self.logDICT = None

    def write(self, jobNAME: str, logDIR: str = None, logSTRING: str = None, logFILE: str = 'log_file.out', logIMAGE: str = 'log_file.png'):
        if logDIR is None:
            pwd = Path.cwd()
            _logDIR = pwd / jobNAME
            _logDIR.mkdir(exist_ok=True)
        else:
            _logDIR = Path(logDIR)

        if logSTRING is not None:
            with open(_logDIR / logFILE, 'a') as ffa:
                print(f"\n{logSTRING}",file=ffa)

        _logFILE = _logDIR / logFILE
        _logIMAGE = _logDIR / logIMAGE

        logDIR = str(_logDIR)

        self.jobNAME = f"JOB: {jobNAME}"
        self.logDIR = logDIR
        self.logFILE = logFILE
        self.logIMAGE = logIMAGE
        self.save_job_JSON()

    def save_job_JSON(self, logDICT: str = None):
        _data = self.home / ".data"
        _data.mkdir(exist_ok=True)
        jobs_file = _data / "JOB_status.json"
        try:
            with open(jobs_file, 'r') as ffr:
                jobs = json.load(ffr)
        except FileNotFoundError:
            jobs = {}
        try:
            jobD = jobs[self.jobNAME]
        except KeyError:
            jobs[self.jobNAME] = {}
            jobD = {}
        if self.logDIR is not None:
            jobD["logDIR"] = self.logDIR
        if self.logFILE is not None:
            jobD["logFILE"] = self.logFILE
        if self.logIMAGE is not None:
            jobD["logIMAGE"] = self.logIMAGE
        if logDICT is not None:
            jobD["logDICT"] = logDICT
        if len(jobD):
            jobs[self.jobNAME] = jobD
            with open(jobs_file, 'w') as ffw:
                json.dump(jobs, ffw, indent=4)


