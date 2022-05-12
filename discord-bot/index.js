require('dotenv').config()
const { Client } = require('discord.js')
const client = new Client()

const express = require('express')
const {spawn} = require('child_process');
const app = express()

client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`)
})

client.on('message', async message => {
    const splitMessage = message.content.split(' ')

    if (splitMessage[0] === '!specklebot') {
        const user = message.user.id
        const command = splitMessage[1]

        if (!command) {
            return
        }
        const result = [];
        const nlp_agent_py = spawn('python', ['nlp_agent_cli.py', user, command]);
        nlp_agent_py.stdout.on('data', function (data) {
            result.push(data);
        });

        await message.reply(result["answer"])
    }
})

client.login(process.env.DISCORD_BOT_TOKEN)
