python-shogi: a pure Python shogi library
=========================================

.. image:: https://travis-ci.org/gunyarakun/python-shogi.svg
    :target: https://travis-ci.org/gunyarakun/python-shogi

.. image:: https://coveralls.io/repos/gunyarakun/python-shogi/badge.svg
    :target: https://coveralls.io/r/gunyarakun/python-shogi

.. image:: https://landscape.io/github/gunyarakun/python-shogi/prototype/landscape.svg?style=flat
    :target: https://landscape.io/github/gunyarakun/python-shogi

.. image:: https://badge.fury.io/py/python-shogi.svg
    :target: https://pypi.python.org/pypi/python-shogi

Introduction
------------

This is the module for shogi written in Pure Python. It's based on python-chess commit 6203406259504cddf6f271e6a7b1e04ba0c96165.

This is the scholars mate in python-shogi:

.. code:: python

    >>> import shogi

    >>> board = shogi.Board()

    >>> board.push(shogi.Move.from_usi('7g7f'))

    >>> board.push_usi('3c3d')
    Move.from_usi('3c3d')
    >>> board.push_usi('8h2b+')
    Move.from_usi('8h2b+')
    >>> board.push_usi('4a5b')
    Move.from_usi('4a5b')
    >>> board.push_usi('B*4b')
    Move.from_usi('B*4b')
    >>> board.push_usi('5a4a')
    Move.from_usi('5a4a')
    >>> board.push_usi('2b3a')
    Move.from_usi('2b3a')
    >>> board.is_checkmate()
    True

Features
--------

* Supports Python 2.7 and Python 3.3+.

* Supports standard shogi (hon shogi)

* Legal move generator and move validation.

  .. code:: python

      >>> shogi.Move.from_usi("5i5a") in board.legal_moves
      False

* Make and unmake moves.

  .. code:: python

      >>> last_move = board.pop() # Unmake last move
      >>> last_move
      Move.from_usi('2b3a')

      >>> board.push(last_move) # Restore

* Show a simple ASCII board.

  .. code:: python

      >>> print(board)
       l  n  s  g  .  k +B  n  l
       .  r  .  .  g  B  .  .  .
       p  p  p  p  p  p  .  p  p
       .  .  .  .  .  .  p  .  .
       .  .  .  .  .  .  .  .  .
       .  .  P  .  .  .  .  .  .
       P  P  .  P  P  P  P  P  P
       .  .  .  .  .  .  .  R  .
       L  N  S  G  K  G  S  N  L
      <BLANKLINE>
       S*1

* Show a KIF style board.

  .. code:: python

      >>> print(board.kif_str())
      後手の持駒：
        ９ ８ ７ ６ ５ ４ ３ ２ １
      +---------------------------+
      |v香v桂v銀v金 ・v玉 馬v桂v香|一
      | ・v飛 ・ ・v金 角 ・ ・ ・|二
      |v歩v歩v歩v歩v歩v歩 ・v歩v歩|三
      | ・ ・ ・ ・ ・ ・v歩 ・ ・|四
      | ・ ・ ・ ・ ・ ・ ・ ・ ・|五
      | ・ ・ 歩 ・ ・ ・ ・ ・ ・|六
      | 歩 歩 ・ 歩 歩 歩 歩 歩 歩|七
      | ・ ・ ・ ・ ・ ・ ・ 飛 ・|八
      | 香 桂 銀 金 玉 金 銀 桂 香|九
      +---------------------------+
      先手の持駒：　銀

* Detects checkmates, stalemates.

  .. code:: python

      >>> board.is_stalemate()
      False
      >>> board.is_game_over()
      True

* Detects repetitions. Has a half move clock.

  .. code:: python

      >>> board.is_fourfold_repetition()
      False
      >>> board.move_number
      8

* Detects checks and attacks.

  .. code:: python

      >>> board.is_check()
      True
      >>> board.is_attacked_by(shogi.BLACK, shogi.A4)
      True
      >>> attackers = board.attackers(shogi.BLACK, shogi.H5)
      >>> attackers
      SquareSet(0b111000010000000000000000000000000000000000000000000000000000000000000000000000)
      >>> shogi.H2 in attackers
      True
      >>> print(attackers)
      . . . . . . . . .
      . . . . . . . . .
      . . . . . . . . .
      . . . . . . . . .
      . . . . . . . . .
      . . . . . . . . .
      . . . . . . . . .
      . . . . . . . 1 .
      . . . 1 1 1 . . .

* Parses and creates USI representation of moves.

  .. code:: python

      >>> board = shogi.Board()
      >>> shogi.Move(shogi.E2, shogi.E4).usi()
      '2e4e'

* Parses and creates SFENs

  .. code:: python

      >>> board.sfen()
      'lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1'
      >>> board.piece_at(shogi.I5)
      Piece.from_symbol('K')

* Read and write KIFs.

  .. code:: python

      >>> import shogi.KIF

      >>> kif = shogi.KIF.Parser.parse_file('data/games/habu-fujii-2006.kif')[0]

      >>> kif['names'][shogi.BLACK]
      '羽生善治'
      >>> kif['names'][shogi.WHITE]
      '藤井猛'
      >>> kif['moves'] # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
      ['7g7f',
       '3c3d',
       ...,
       '9a9b',
       '7a7b+']
      >>> kif['win']
      'b'

* Communicate with a CSA protocol.

  Please see `random_csa_tcp_match <https://github.com/gunyarakun/python-shogi/blob/master/scripts/random_csa_tcp_match>`_.

* Parse professional shogi players' name

      >>> import shogi.Person

      >>> shogi.Person.Name.is_professional('羽生　善治 名人・棋聖・王位・王座')
      True

Peformance
----------
python-shogi is not intended to be used by serious shogi engines where
performance is critical. The goal is rather to create a simple and relatively
highlevel library.

You can install the `gmpy2` or `gmpy` (https://code.google.com/p/gmpy/) modules
in order to get a slight performance boost on basic operations like bit scans
and population counts.

python-shogi will only ever import very basic general (non-shogi-related)
operations from native libraries. All logic is pure Python. There will always
be pure Python fallbacks.

Installing
----------

* With pip:

  ::

      sudo pip install python-shogi

* From current source code:

  ::

      python setup.py sdist
      sudo python setup.py install

How to test
-----------

::

  > nosetests
  or
  > python setup.py test # requires python setup.py install

If you want to print lines from the standard output, execute nosetests like following.

::

  > nosetests -s

If you want to test among different Python versions, execute tox.

::

  > pip install tox
  > tox

ToDo
----

- Support USI protocol.

- Support board.generate_attacks() and use it in board.is_attacked_by() and board.attacker_mask().

- Remove rotated bitboards and support `Shatranj-style direct lookup
  <http://arxiv.org/pdf/0704.3773.pdf>`_ like recent python-chess.

- Support %MATTA etc. in CSA TCP Protocol.

- Support board.is_pinned() and board.pin().

本リポジトリについて
=====================

- 本リポジトリは、python-shogi https://github.com/gunyarakun/python-shogi をforkしました。

- python-shogi ライブラリをを一部変更しています。

- USIエンジンからCSAプロトコルで通信するためのスクリプト scripts/csa_usi_bridge.py が含まれています。

- 第5回電王トーナメント http://denou.jp/tournament2017/ (以下、std5)に出場した Yorkie は、scripts/csa_usi_bridge.py を使い、Linux PC上で X server を止めた状態で対局しました。

CSA USI bridgeでできること
-----------------------

- USIエンジンを使ったCSAプロトコルでの対局

- USIエンジン起動時に、テキストファイルの内容に基づいたsetoptionをUSIエンジンに送る。

- CUIでの局面表示::

    l  n  s  g  k  g  s  n  l
    .  r  .  .  .  .  .  b  .
    p  p  p  p  p  p  p  p  p
    .  .  .  .  .  .  .  .  .
    .  .  .  .  .  .  .  .  .
    .  .  .  .  .  .  .  .  .
    P  P  P  P  P  P  P  P  P
    .  B  .  .  .  .  .  R  .
    L  N  S  G  K  G  S  N  L
    B(self): 300.0 W: 300.0
    USI>  position lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1
    USI>  go btime 310000 wtime 300000 byoyomi 0
    USI<  info pv 7g7f 3c3d (100.00%) score cp 0 depth 0 multipv 1
    USI<  bestmove 7g7f ponder 3c3d
    USI>  position lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1 moves 7g7f 3c3d
    USI>  go ponder

- 残り時間の表示

- CSAサーバーに対して、評価値や読み筋や評価局面数の送信(std5形式)

- 双方の指し手と消費時間の記録

- 途中の局面からの対局

CSA USI bridgeでできないこと、できないかもしれないこと
--------------------------------------------

- ponder思考時のパイプ処理を手抜きしているので、ponderでの思考時、OSのパイプのバッファにテキストがたまりまくる。したがって、ponder思考時にUSIエンジンからのテキスト出力が大量になると、とりこぼすかも。Linuxのデフォルト設定で、YaneuraOuくらいのテキスト出力量だと、1回のponder思考時間が３〜6時間くらいまでは大丈夫だと思うが、テキスト出力が多めのUSIエンジンだったり、パイプのバッファが小さめのOSだときついかも。

- USIエンジンが出力する文字コードをUTF-8と決め打ちしているので、他の文字コードだと文字化けしたり、落ちたりするかも。

- python-shogi ライブラリへの変更点は、Python2系列と3系列でテストしてるけど、scripts/csa_usi_bridge.py は Python3系列でしか試してないので、2系列だとダメかも。

- 対局が終わるとスクリプトが終了するので、連続対局できない。

- CSA拡張モードに対応していない。

- 自分の手を送る時のコメントの仕様について、std5ルールだけに合わせている。

- USIエンジンがどの深さまで読んでいても、読み筋として1手しか送っていない。

std5版との違い
---------------------

- std5では、使用可能な python-shogi ライブラリとしてVer1.0.4が指定されていたので、Ver1.0.4を元にしてIssueの#7, #8, #9を自前で修正し、その状態の python-shogi ライブラリを前提に scripts/csa_usi_bridge.py を作成しました。一方で本リポジトリでは、Issue #7, #8, #9をすべて修正済みのVer1.0.6からforkし、その状態の python-shogi ライブラリを前提にした scripts/csa_usi_bridge.py としました。

- std5の scripts/csa_usi_bridge.py は、USIエンジンを Yorkie に決め打ちしていた一方、本リポジトリでは引数でUSIエンジンを指定できるようにしています。

- std5の scripts/csa_usi_bridge.py で局面表示時、駒を漢字で表示していた一方、本リポジトリでは駒を英字で表示しています。

その他
------

- 本リポジトリでpython-shogi ライブラリに対して変更した箇所のうち、割と汎用的に使えそうな部分は、fork元に pull request しているので、とりこんでもらえるかも。
