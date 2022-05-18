require('dotenv').config()
const { Client, Intents } = require('discord.js');
const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] });
const express = require('express');
const {spawn} = require('child_process');
const axios = require('axios');
const httpTerminator = require('http-terminator');


const app = express();
const port = 3000;

client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`)
})

let userName;
let userRequest;
let channelID;
let running = false;
let runningID = '';

client.on('messageCreate', async message => {
    const messageContent = message.content;
    const splitMessage = messageContent.split(' ')

    if (running && message.id != runningID) {
        // console.log(message.id);
        // console.log(runningID);
        // await message.reply("Sorry, I'm busy now! try again later, please.");
        return
    }

    if (splitMessage[0].toLowerCase() === '!speckly') {
        running = true;
        runningID = message.id
        userName = message.author.username;
        channelID = message.channelId;
        userRequest = messageContent.substring(messageContent.indexOf(' ') + 1);

        let result;
        app.get('/', (req, res) => {
            const nlp_agent_py = spawn('python', ['-m', 'nlp_agent_cli', userName, userRequest, channelID]);
            nlp_agent_py.stdout.on('data', function (data) {
                result = data.toString();
            });
            nlp_agent_py.on('close', (code) => {
                console.log(result);
                res.send(result);
            });
        })
        const server = await app.listen(
            port,() => console.log(`Message received from ${userName}!\n  -> "${userRequest}"`)
        );

        await axios.get(`http://localhost:${port}/`)
            .then(response => {
                result = response.data;
            })
            .catch(e => {
                console.log(e);
            });

        await message.reply(result["answer"]);

        const httpTerminatorElm = httpTerminator.createHttpTerminator({
            server,
        });
        await httpTerminatorElm.terminate();
        console.log(`Request from ${userName} answered`);
        running = false;
    }
})

client.login(process.env.DISCORD_BOT_TOKEN)
