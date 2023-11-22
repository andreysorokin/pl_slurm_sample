import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

from pathlib import Path
import time
import torch

from lightning.pytorch.demos import WikiText2, Transformer
import lightning as L
import torch.nn as nn

from jsonargparse import CLI
from dataclasses import dataclass


@dataclass
class Settings:
    num_nodes: int = 1
    devices: int = 1
    batch_size: int = 32
    resume: bool = True


def build_model(vocab_size):
    return Transformer(
        vocab_size=vocab_size,
        ninp=200,
        nhead=2,
        nhid=200,
        nlayers=2
    )


def main(fabric: L.Fabric, s: Settings):
    out_dir = Path("/shared/")
    fabric.seed_everything(42)

    with fabric.rank_zero_first():
        dataset = WikiText2()

    dataloader = torch.utils.data.DataLoader(dataset, batch_size=s.batch_size)
    dataloader = fabric.setup_dataloaders(dataloader)

    with fabric.init_module(empty_init=False):
        model = build_model(dataset.vocab_size)

    model = fabric.setup_module(model)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.1)
    optimizer = fabric.setup_optimizers(optimizer)

    state = {"model": model, "optimizer": optimizer, "iter_num": 0}

    resume = s.resume
    if resume is True:
        checkpoints = out_dir.glob("*.pth")
        if any(checkpoints):
            checkpoints = out_dir.glob("*.pth")
            resume = max(checkpoints, key=lambda p: int(p.name.split("-")[1]))
        else:
            resume = False

    if resume:
        fabric.print(f"Resuming training from {resume}")
        fabric.load(resume, state)

    num_epochs = 3
    for epoch in range(num_epochs):
        for batch in dataloader:
            t0 = time.perf_counter()
            input, target = batch
            optimizer.zero_grad()
            output = model(input, target)
            loss = torch.nn.functional.nll_loss(output, target.view(-1))
            fabric.backward(loss)
            optimizer.step()
            t1 = time.perf_counter()

            fabric.print(
                f"{epoch}/{num_epochs}, Step: {state['iter_num']}/{len(dataloader)}, : batch_size: {s.batch_size} | Train Epoch Loss: {loss}, step took {(t1 - t0) * 1000:.2f}ms")
            state["iter_num"] += 1

            if state["iter_num"] % 10 == 0:
                checkpoint_path = out_dir / f"iter-{state['iter_num']:07d}-ckpt.pth"
                fabric.print(f"Saving checkpoint to {str(checkpoint_path)!r}")
                fabric.save(checkpoint_path, state)


layers = {
    nn.TransformerEncoderLayer,
    nn.TransformerDecoderLayer,
}

if __name__ == "__main__":
    s = CLI(Settings, as_positional=False)
    fabric = L.Fabric(num_nodes=s.num_nodes, devices=s.devices)
    fabric.launch(main, s)
