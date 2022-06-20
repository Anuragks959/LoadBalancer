import json

from flask import Flask, jsonify, request
import random
from random import choices

import flask

import uncurl

app = Flask(__name__)

serverName = "GA-server"

servers = 5

serverVector = [[10, 55], [2, 10], [5, 30], [7, 40], [5, 30]]

nicArray = []

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


# def fitness(ind):
#     return random.randint(0, 100)

def fitness(soln):
    n = len(soln)
    # requests=
    fitvalue = 0
    for itr in range(n):
        nic = nicArray[itr]
        fitvalue += serverVector[soln[itr]][1] * nic / serverVector[soln[itr]][0]
    return fitvalue


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
    generations = 10
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


@app.route('/batch', methods=['POST'])
def batchProcess():
    g = flask.request
    body = g.get_json()
    reqs = body['batch']
    n = len(reqs)
    global nicArray
    for curl in reqs:
        parseCurl = uncurl.parse_context(curl) #-- get header
        nic = (parseCurl.headers)['nic']
        nicArray.append(float(nic))
    initPop = ransol(n)
    tbr = json.dumps(geneticAlgo(initPop))
    nicArray = []
    return tbr


if __name__ == '__main__':
    app.run(port=5050)