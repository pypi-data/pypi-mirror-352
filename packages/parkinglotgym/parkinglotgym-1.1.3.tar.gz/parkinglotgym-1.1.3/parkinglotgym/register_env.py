from gymnasium.envs.registration import register

register(
    id='Puzzle6x6Moves60-v0',
    entry_point='parkinglotgym.parking_lot_env:ParkingLotEnv',
    kwargs={
        'layout_str_or_moves': 60
    }
)

register(
    id='Puzzle6x6Moves30-v0',
    entry_point='parkinglotgym.parking_lot_env:ParkingLotEnv',
    kwargs={
        'layout_str_or_moves': 30
    }
)

register(
    id='Puzzle6x6Moves15-v0',
    entry_point='parkinglotgym.parking_lot_env:ParkingLotEnv',
    kwargs={
        'layout_str_or_moves': 15
    }
)

register(
    id='Puzzle6x6Moves10-v0',
    entry_point='parkinglotgym.parking_lot_env:ParkingLotEnv',
    kwargs={
        'layout_str_or_moves': 10
    }
)

register(
    id='Puzzle6x6Moves5-v0',
    entry_point='parkinglotgym.parking_lot_env:ParkingLotEnv',
    kwargs={
        'layout_str_or_moves': 5
    }
)

register(
    id='Puzzle6x6Moves3-v0',
    entry_point='parkinglotgym.parking_lot_env:ParkingLotEnv',
    kwargs={
        'layout_str_or_moves': 3
    }
)

register(
    id='Puzzle6x6Moves13Fixed-v0',
    entry_point='parkinglotgym.parking_lot_env:ParkingLotEnv',
    kwargs={
        'layout_str_or_moves': """
        .BBBCC
        DDEEJK
        AAI.JK
        H.IFFL
        H....L
        GGG..L
        """
    }
)

register(
    id='Puzzle6x6Moves6Fixed-v0',
    entry_point='parkinglotgym.parking_lot_env:ParkingLotEnv',
    kwargs={
        'layout_str_or_moves': """
        ..BBBG
        ...EFG
        AA.EFG
        ...E#.
        .DDD..
        ......
        """
    }
)

register(
    id='Puzzle6x6Moves3Fixed-v0',
    entry_point='parkinglotgym.parking_lot_env:ParkingLotEnv',
    kwargs={
        'layout_str_or_moves': """
        .BBB..
        ...C..
        AA.C..
        ...D..
        ...D..
        ...D..
        """
    }
)