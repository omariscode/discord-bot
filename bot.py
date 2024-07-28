import discord
from discord.ext import commands
import subprocess
import os
import tempfile
import logging
import re

TOKEN = 'MTI1OTE4OTM1OTM2MjcwNzYwMA.GEensZ.cjTrbUZ7AG4z0uGJyAmsYmILzK5n60ERy6msmg'

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

def identify_language(code):
    patterns = {
        'python': r'^\s*print\s*\(',
        'javascript': r'^\s*console\.log\s*\(',
        'cpp': r'^\s*#include\s+<',
        'java': r'^\s*public\s+class\s+\w+\s*{',
        'csharp': r'^\s*(using|namespace|class|public|private|static)\s+',
        'php': r'^\s*<\?php'
    }

    for lang, pattern in patterns.items():
        if re.search(pattern, code, re.MULTILINE):
            return lang

    return 'unknown'

def translate_errors(error_messages, lang):
    translated_errors = []

    if lang == 'python':
        for error in error_messages:
            if 'SyntaxError' in error:
                error_msg = re.search(r'^  File ".+", line (\d+)\n    (.+)\n', error, re.MULTILINE)
                if error_msg:
                    line_number = error_msg.group(1)
                    error_text = error_msg.group(2)
                    translated_errors.append(f'Erro de sintaxe na linha {line_number}: {error_text}')
                else:
                    translated_errors.append(f'Erro de sintaxe: {error}')
            elif 'NameError' in error:
                translated_errors.append(f'Erro de nome: {error}')
            # I could add more condition for other error for Python
    elif lang == 'javascript':
        for error in error_messages:
            if 'SyntaxError' in error:
                translated_errors.append(f'Erro de sintaxe: {error}')
            elif 'ReferenceError' in error:
                translated_errors.append(f'Erro de referência: {error}')
            # I could add more condition for other error for JavaScript
    elif lang == 'cpp':
        for error in error_messages:
            if 'error:' in error:
                translated_errors.append(f'Erro de compilação: {error}')
            # I could add more condition for other error for C++
    elif lang == 'java':
        for error in error_messages:
            if 'error:' in error:
                translated_errors.append(f'Erro de compilação: {error}')
            # I could add more condition for other error for Java
    elif lang == 'csharp':
        for error in error_messages:
            if 'error ' in error:  # Ajustado para lidar com diferentes tipos de erros em C#
                translated_errors.append(f'Erro de compilação: {error}')
            # I could add more condition for other error for C#
    elif lang == 'php':
        for error in error_messages:
            if 'Parse error' in error:
                translated_errors.append(f'Erro de análise: {error}')
            elif 'Fatal error' in error:
                translated_errors.append(f'Erro fatal: {error}')
            # I could add more condition for other error for PHP

    return translated_errors

@bot.command()
async def debug(ctx, *, code):
    lang = identify_language(code)
    temp_file_name = f'{tempfile.mktemp()}.{lang}'

    with open(temp_file_name, 'w') as temp_file:
        temp_file.write(code)

    try:
        if lang == 'python':
            result = subprocess.run(['python3', '-m', 'pylint', temp_file_name], capture_output=True, text=True)
        elif lang == 'javascript':
            result = subprocess.run(['node', '--check', temp_file_name], capture_output=True, text=True)
        elif lang == 'cpp':
            result = subprocess.run(['g++', '-fsyntax-only', temp_file_name], capture_output=True, text=True)
        elif lang == 'java':
            result = subprocess.run(['javac', temp_file_name], capture_output=True, text=True)
        elif lang == 'php':
            result = subprocess.run(['php', '-l', temp_file_name], capture_output=True, text=True)
        elif lang == 'csharp':
            result = subprocess.run(['csc', temp_file_name], capture_output=True, text=True)
        else:
            await ctx.send(f'Linguagem de programação não suportada: {lang}')
            os.remove(temp_file_name)
            return

        error_messages = result.stderr.splitlines() if result.stderr else result.stdout.splitlines()
        translated_errors = translate_errors(error_messages, lang)

        if translated_errors:
            errors_text = "\n".join(translated_errors)
            await ctx.send(f'Erro(s) encontrado(s):\n```{errors_text}```')
        else:
            await ctx.send(f'Código está correto!')

    except Exception as e:
        logging.error(f'Error processing code: {e}')
        await ctx.send(f'Erro ao processar código: {e}')
    finally:
        os.remove(temp_file_name)

bot.run(TOKEN)
