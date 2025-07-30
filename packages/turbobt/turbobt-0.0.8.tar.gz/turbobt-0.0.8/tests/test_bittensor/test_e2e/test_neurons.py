import ipaddress
import pytest
import pytest_asyncio

import turbobt
from turbobt.subtensor.exceptions import (
    HotKeyAlreadyRegisteredInSubNet,
    NotEnoughBalanceToStake,
)


@pytest_asyncio.fixture
async def subnet(bittensor, alice_wallet):
    subnet = bittensor.subnet(2)

    # try:
    #     await bittensor.subnets.register(
    #         alice_wallet,
    #     )
    # except NotEnoughBalanceToStake:
    #     pass

    return subnet


@pytest.mark.asyncio
async def test_serve(subnet, alice_wallet):
    try:
        await subnet.neurons.register(alice_wallet.hotkey, wallet=alice_wallet)
    except HotKeyAlreadyRegisteredInSubNet:
        pass

    await subnet.neurons.serve(
        ip="192.168.0.2",
        port=1983,
        certificate=b"MyCert",
    )

    neurons = await subnet.list_neurons()
    neuron = neurons[0]

    assert neuron.axon_info.ip == ipaddress.IPv4Address("192.168.0.2")
    assert neuron.axon_info.port == 1983

    cert = await subnet.neuron(
        hotkey=alice_wallet.hotkey.ss58_address
    ).get_certificate()

    assert cert == {
        "algorithm": 77,
        "public_key": "yCert",
    }


@pytest.mark.asyncio
async def test_asso(bittensor: turbobt.Bittensor):
    subnet = bittensor.subnet(12)

    asso = await bittensor.subtensor.subtensor_module.AssociatedEvmAddress.query(
        12,
    )
    asso = await subnet.evm_addresses.fetch()

    assert len(asso) == 0
