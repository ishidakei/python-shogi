# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import re
import subprocess
import os
import sys
import shogi
from shogi import CSA
from shogi import Move

class CSAUSIBrdige:
    if not hasattr(sys.stdout, 'buffer'):
        import locale
        import codecs
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

    def __init__(self, usi_engine_path):
        self.proc = subprocess.Popen(usi_engine_path,
                                     bufsize=0,
                                     shell=False,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     )
        self.write_usi("usi\n")
        while True:
            output = self.read_usi_line()
            if output.rstrip() == "usiok":
                break
        usi_options_path = './usioptions.txt'
        if os.path.exists(usi_options_path):
            with open(usi_options_path, "r") as options:
                for line in options:
                    self.write_usi(line)
        self.write_usi("isready\n")
        while True:
            output = self.read_usi_line()
            if output.rstrip() == "readyok":
                break

    def connect(self, host_name, user_name, password):
        print("CONNECTING...")
        self.csa = CSA.TCPProtocol(host_name, 4081)
        self.csa.login(user_name, password)
        print("CONNECTED")

    node_re = re.compile("nodes +([0-9]+)")
    cp_re = re.compile("cp +(\-?[0-9]+)")
    ponder_re = re.compile("ponder +([0-9a-zA-Z\*\+]+)")
    bestmove_re = re.compile("bestmove +([0-9a-zA-Z\*\+]+)")

    def game(self, log = None):
        moves = []
        btime = 900000
        wtime = 900000
        byoyomi = 10000
        time_increment = 0
        print("WAITING FOR MATCHING...")
        game_summary = self.csa.wait_match()
        print("MATCHED")
        start_sfen = game_summary['summary']['sfen']
        my_color = game_summary['my_color']
        time = game_summary['summary']['time']
        if time != None:
            if time['Total_Time'] != None:
                btime = int(time['Total_Time']) * 1000
                wtime = btime
            if time['Byoyomi'] != None:
                byoyomi = int(time['Byoyomi']) * 1000
            if time['Increment'] != None:
                time_increment = int(time['Increment']) * 1000
        board = shogi.Board(start_sfen)
        for move in game_summary['summary']['moves']:
            if move['color'] == 0:
                btime += time_increment - float(move['spend_time']) * 1000
            else:
                wtime += time_increment - float(move['spend_time']) * 1000
            board.push(shogi.Move.from_usi(move['usi']))
        self.csa.agree()
        self.write_usi("usinewgame\n")
        ponder = None
        ponder_hit = None
        while True:
            print(board)
            if my_color == 0:
                print('B(self):', btime / 1000, 'W:', wtime / 1000)
            else:
                print('B:', btime / 1000, 'W(self):', wtime / 1000)

            if board.turn == my_color:
                if my_color == 0:
                    btime += time_increment
                else:
                    wtime += time_increment
                nodes = 0
                cp = 0
                ponder = None
                bestmove = None
                if ponder_hit == None:
                    if len(moves) == 0:
                        self.write_usi("position {0}\n".format(start_sfen))
                    else:
                        self.write_usi("position {0} moves {1}\n".format(start_sfen, " ".join(moves)))
                    self.write_usi("go btime {0} wtime {1} byoyomi {2}\n".format(
                        btime,
                        wtime,
                        byoyomi
                    ))
                while True:
                    output = self.read_usi_line()
                    if output[0:5] == "info ":
                        match = self.node_re.search(output)
                        if match != None:
                            nodes = int(match.group(1))
                        match = self.cp_re.search(output)
                        if match != None:
                            cp = int(match.group(1))
                    if output[0:9] == "bestmove ":
                        match = self.ponder_re.search(output)
                        if match != None:
                            ponder = match.group(1)
                        if output[0:12] == "bestmove win":
                            self.csa.command('%KACHI')
                            break
                        if output[0:15] == "bestmove resign":
                            self.csa.resign()
                            break
                        match = self.bestmove_re.search(output)
                        if match != None:
                            bestmove = match.group(1)
                            break
                if bestmove != None:
                    next_move = Move.from_usi(bestmove)
                    board.push(next_move)
                    moves.append(bestmove)
                    if ponder != None:
                        self.write_usi("position {0} moves {1} {2}\n".format(
                            start_sfen,
                            ' '.join(moves),
                            ponder
                        ))
                        self.write_usi("go ponder\n")
                    if my_color != 0:
                        cp = -cp
                    comment = "\'* {0}".format(cp)
                    if ponder != None:
                        comment = comment + " {0}".format(Move.from_usi(ponder))
                    comment = comment + " #{0}".format(nodes)
                    line = self.csa.move(board.pieces[next_move.to_square], my_color, next_move, comment)
                    while True:
                        if line[0] == '+' or line[0] == '-':
                            (turn, usi, spend_time, message) = self.csa.parse_server_message(line, board)
                            if my_color == 0:
                                btime = max(0, btime - int(spend_time * 1000))
                            else:
                                wtime = max(0, wtime - int(spend_time * 1000))
                            self.show_and_log("SELF MOVE: {0}{1},T{2},{3}".format("+" if turn == 0 else "-",
                                                                                  next_move,
                                                                                  spend_time,
                                                                                  comment,
                                                                                  ),
                                              log)
                            break
                        self.show_and_log("MESSAGE: {0}".format(line),
                                          log)
                        line = self.csa.read_line()
            else:
                if my_color == 1:
                    btime += time_increment
                else:
                    wtime += time_increment
                ponder_hit = None
                (turn, usi, spend_time, message) = self.csa.wait_server_message(board)
                if message is not None:
                    self.show_and_log("MESSAGE: {0}".format(CSA.SERVER_MESSAGE_SYMBOLS[message]),
                                      log)
                    if message == CSA.WIN:
                        break
                    elif message == CSA.LOSE:
                        break
                    elif message == CSA.CENSORED:
                        break
                    elif message == CSA.CHUDAN:
                        break
                else:
                    if turn != board.turn:
                        raise ValueError("Invalid turn")
                    if my_color == 1:
                        btime = max(0, btime - int(spend_time * 1000))
                    else:
                        wtime = max(0, wtime - int(spend_time * 1000))
                    move = shogi.Move.from_usi(usi)
                    self.show_and_log("OPPONENT MOVE: {0}{1},T{2}".format("+" if turn == 0 else "-",
                                                                          move,
                                                                          spend_time,
                                                                          ),
                                      log)
                    if ponder != None:
                        if ponder != usi:
                            self.write_usi("stop\n")
                            while True:
                                output = self.read_usi_line()
                                if output[0:9] == "bestmove ":
                                    break
                        else:
                            self.write_usi("ponderhit\n")
                            ponder_hit = True
                    board.push(move)
                    moves.append(usi)

    def write_usi(self, str):
        self.proc.stdin.write(str.encode("utf-8"))
        print("USI> ", str.rstrip())

    def read_usi_line(self):
        line = self.proc.stdout.readline().decode("utf-8")
        print("USI< ", line.rstrip())
        return line

    def show_and_log(self, str, log):
        print(str)
        if log is not None:
            log.write("{0}\n".format(str))

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc != 5:
        print('Usage: {0} usi_engine host_name user_name password'.format(sys.argv[0]))
        sys.exit(1)
    bridge = CSAUSIBrdige(sys.argv[1])
    bridge.connect(sys.argv[2], sys.argv[3], sys.argv[4])
    with open("log.txt", "w") as log:
        bridge.game(log)
