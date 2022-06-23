import json
import requests
from flask import Flask, jsonify, request
import random
from random import choices
import asyncio

import aiohttp

import flask

import uncurl

app = Flask(__name__)

serverName = "GA-server"

servers = 5

serverVector = [[10, 2000], [2, 1500], [3, 1700], [7, 1600], [5, 800]]

serversList = ["http://127.0.0.1:5001","http://127.0.0.1:5002","http://127.0.0.1:5003","http://127.0.0.1:5004","http://127.0.0.1:5005"]

normalizationFactor = 100000000

nicArray = []

responseArray = []
# MIPS, CostOfOperation

def ransol(n):
    popSize = 10
    l = []
    for i in range(popSize):
        s = []
        for j in range(n):
            c = random.randint(0, (servers - 1))
            s.append(c)
        l.append(s)
    return l


def fitness(soln):
    n = len(soln)
    fitvalue = 0
    for itr in range(n):
        nic = nicArray[itr]
        fitvalue += (serverVector[soln[itr]][1] * nic) / serverVector[soln[itr]][0]
    return normalizationFactor-fitvalue


def pick_parent_candidates(g):
    popu = g.copy()
    fitnesses = [fitness(j) for j in popu]
    p1 = choices(popu, weights=fitnesses, k=1)[0]
    ii = popu.index(p1)
    popu.pop(ii)
    fitnesses.pop(ii)
    p2 = choices(popu, weights=fitnesses, k=1)[0]
    return [list(p1)] + [list(p2)]


def crossover(par1, par2):
    cp = len(par1)
    o1 = []
    o2 = []
    cc = 0.6
    for i in range(0, cp):
        getrand = random.random()
        if getrand > cc:
            o1.append(par1[i])
            o2.append(par2[i])
            continue
        o1.append(par2[i])
        o2.append(par1[i])
    return [o1, o2]


def getrndserver(i):
    rt = random.randint(0, servers-1)
    while rt == i:
        rt = random.randint(0, servers-1)
    return rt


def mutation2(off):
    canmut = 0.1
    tbr = []
    for i in range(len(off)):
        getrand = random.random()
        if getrand > canmut:
            tbr.append(off[i])
            continue
        tbr.append(getrndserver(i))
    return tbr


def geneticAlgo(ip):
    population = ip.copy()
    generations = 100
    for i in range(generations + 1):
        a, b = pick_parent_candidates(population)
        oa, ob = crossover(a, b)
        oa = mutation2(oa)
        ob = mutation2(ob)
        population.append(oa)
        population.append(ob)
        population.sort(key=fitness, reverse=True)
        population.pop()
        population.pop()

    return population[0]


@app.route('/', methods=['GET'])
def hello():
    return serverName

async def getResponse(session,destUrlAssign,nic):
    async with session.get(destUrlAssign, headers={'nic':nic}) as resp:
        pokemon = await resp.read()
        my_json = pokemon.decode('utf8')
        hashrate = json.dumps(my_json)
        return hashrate

async def getResponses(curls, assignment):
    global responseArray

    async with aiohttp.ClientSession() as session:

        tasks = []
        
        for i in range(len(curls)):
            curl = curls[i]
            rawReq = uncurl.parse_context(curl)
            nic = (rawReq.headers)['nic']
            serverUrl = serversList[assignment[i]]
            destUrlAssign = serverUrl + rawReq.url
            tasks.append(asyncio.ensure_future(getResponse(session,destUrlAssign,nic)))
            # tasks.append(loop.create_task(getResponse(destUrlAssign,nic)))#requests.get(destUrlAssign, headers={'nic':nic})))

        original_pokemon = await asyncio.gather(*tasks)
        for pokemon in original_pokemon:
            responseArray.append(pokemon)

def initiateNormalFactor():
    v = 0
    global nicArray
    maxNic=max(nicArray)
    for svr in serverVector:
        v += svr[1]*(maxNic+1)
    global normalizationFactor
    normalizationFactor=max([v,normalizationFactor])

@app.route('/batch', methods=['POST'])
def batchProcess():
    g = flask.request
    body = g.get_json()
    reqs = body['batch']
    n = len(reqs)
    global nicArray
    global responseArray
    for curl in reqs:
        parseCurl = uncurl.parse_context(curl) #-- get header
        nic = (parseCurl.headers)['nic']
        nicArray.append(float(nic))
    initiateNormalFactor()
    initPop = ransol(n)
    assignment = geneticAlgo(initPop)

    # responseArray = getResponses(body['batch'], assignment)
    asyncio.run(getResponses(body['batch'], assignment))
    # responseArray =asyncio.run(reqCall(body['batch'], assignment))

    nicArray = []

    tbr = responseArray.copy()
    responseArray = []

    return json.dumps(tbr)


if __name__ == '__main__':
    app.run(port=5050)