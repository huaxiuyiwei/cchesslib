# -*- coding: utf-8 -*-
'''
Copyright (C) 2014  walker li <walker8088@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import os, sys, time
from pathlib import Path
from cchess import *

result_dict = {'红胜': RED_WIN, '黑胜': BLACK_WIN, '和棋': PEACE}


def load_move_txt(txt_file):
    with open(txt_file, "rb") as f:
        lines = f.readlines()
    fen = lines[0].strip().decode('utf-8')
    moves = [it.strip().decode('utf-8') for it in lines[1:-1]]
    result = result_dict[lines[-1].strip().decode('utf-8')]
    return (fen, moves, result)


class TestUCCI():
    def setup(self):
        os.chdir(os.path.dirname(__file__))
        self.engine = UcciEngine()
        self.engine.load("..\\ucci_engines\\eleeye\\eleeye.exe")

    def teardown(self):
        pass

    def test_ucci(self):
        fen, moves, result = load_move_txt(Path("data", "ucci_test1_move.txt"))
        game = read_from_xqf(Path('data', 'ucci_test1.xqf'))
        game.init_board.move_side = ChessSide.RED

        assert game.init_board.to_fen() == fen
        assert game.info['Result'] == result
        board = game.init_board.copy()

        dead = False
        while not dead:
            self.engine.go_from(board.to_fen(), 8)
            while True:
                self.engine.handle_msg_once()
                if self.engine.move_queue.empty():
                    time.sleep(0.2)
                    continue
                output = self.engine.move_queue.get()
                if output[0] == 'best_move':
                    p_from, p_to = output[1]["move"]
                    move_str = board.move(p_from, p_to).to_chinese()
                    assert move_str == moves.pop(0)
                    last_side = board.move_side
                    board.next_turn()
                    break
                elif output[0] == 'dead':
                    if board.move_side == ChessSide.RED:
                        assert result == BLACK_WIN
                    else:
                        assert result == RED_WIN
                    dead = True
                    break
                elif output[0] == 'draw':
                    dead = True
                    break
                elif output[0] == 'resign':
                    if board.move_side == ChessSide.RED:
                        assert result == BLACK_WIN
                    else:
                        assert result == RED_WIN
                    dead = True
                    break

        self.engine.quit()
        time.sleep(0.5)
