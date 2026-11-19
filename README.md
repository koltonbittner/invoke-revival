# Invoke Revival

At roughly $35 used, a discontinued Harman Kardon Invoke gets you a high quality speaker setup, a microphone array, and an ARM processor that can run community firmware. I bought three for $105. The hardware made sense at that price because I could use the same units for discrete TV surround, synchronized music playback, and room-aware voice control. The left rear speaker doubles as an audio analyzer for music-reactive home scenes.

Two Invokes sit behind the listening position in the bedroom. The third is in the kitchen. Where the audio gets processed depends on what’s playing.

| Workload | Signal path |
| --- | --- |
| TV surround | The LG extracts surround-left and surround-right before its stereo downmix and sends them to the rear pair over Bluetooth. The TV plays the front mix. |
| Multiroom music | Spotify on my phone sends audio to the selected AirPlay 2 group. Each Invoke runs Shairport Sync with NQPTP for timing. |
| Music scene animations | The left Invoke extracts features from digital playback PCM. A Mac running Linux maps those features to lamp commands. |
| Voice | Each Invoke acts as a Wyoming satellite. The Linux host handles wake-word and speech processing, and Home Assistant uses the originating room to resolve the command and route the response. |

## Extracting discrete surround channels on the TV

The important decision was where to tap the signal. Once the LG has downmixed a multichannel soundtrack to stereo, the Bluetooth output no longer carries independently addressable surround channels. I take surround-left and surround-right from the decoder upstream of that downmix, preserve their channel order, and route them to the two Invokes. Stereo sources have no discrete rear pair to extract.

I first routed the rear channels through a Linux bridge. After correcting a left/right swap, I ran eight channel-identification probes. All eight played from the intended physical speaker.

I then moved the adapter onto the TV and tested digital delivery into its Bluetooth buffer. In roughly 234 seconds the adapter rendered **10,978 blocks**. The counters recorded **three startup undersupplies, zero source faults, and zero native capture errors**. Front-to-rear acoustic delay remains unmeasured.
## AirPlay 2 receiver changes

I built two changes against the RTSP handler in **Shairport Sync 5.6.3** and verified the same patched build directly on all three Invokes.

**Event socket ownership.** While debugging intermittent grouping failures, I found seven listening sockets on one receiver and thirteen on another. Each receiver had a 30-port allocation. The event worker owned the accepted connection, but its listening socket had a separate lifetime and survived session teardown. I changed teardown to join the event worker and close the listener, including when the worker had been cancelled while waiting in `accept()`. On the deployed ARM build, the receiver reused a single listener port across 36 consecutive control-session setup/teardown cycles with no audio stream. [Cleanup patch](patches/event-listener-cleanup.patch)

**Capability negotiation.** The phone sometimes requested receiver capabilities in the initial control `SETUP`. I made the handler recognize the boolean `combinedGetInfoWithControlSetup` flag and include the dictionary generated for `GET /info` in the binary plist response. I compared the two responses, checked the advertised lossless capability, and verified that false, absent, and invalid flags preserved the ordinary setup response. [Capability patch](patches/combined-info.patch) · [Verification notes](patches/README.md)

During testing I could form the bedroom group in Apple Podcasts and retain it across Spotify restarts. That observation covers the combined configuration. I didn’t isolate the effect of each change or measure inter-speaker skew.

## Music playback and scene control

I used Music Assistant to group the rear pair successfully. I retired it because Spotify on my phone already lets me select the bedroom pair, the kitchen speaker, or all three through the AirPlay picker. Direct AirPlay kept the grouping I wanted and removed the coordinator from the playback path.

For the lighting, I split feature extraction from rendering. The left Invoke reads digital playback PCM and emits four values: RMS level plus bass, mid, and treble levels. The extractor is configured for 20 updates per second. The Linux Mac consumes those values, renders the animation, and sends commands to lights.

## Room-aware voice routing

All three satellites use the “Orbit” wake word and have explicit room assignments. The room travels with the request, so the same utterance can address different devices depending on which microphone heard it. Device commands return a short chime. Spoken responses, such as the time, go back through the originating Invoke.

I track potential wake events while the TV is playing. Estimating a false-wake rate still needs a longer observation window.

## Native EQ and readback

The firmware accepts a complete EQ object on every write. Two controls reading the same snapshot can overwrite each other even if they touch different fields. In the Home Assistant integration I serialize edits per speaker, read the current object, modify one field, write the full payload, and verify the readback.

The standalone payload builder deep-copies the current object so a tone adjustment preserves the nested room filters. Bass and treble accept integral values from −12 to +12 dB. Loudness and night mode require booleans. The comparison step accounts for a firmware serialization quirk: an unused filter list can read as `null` before the first write and `[]` afterward. Treating those as equivalent avoids reporting a failed write when the saved EQ is unchanged. [Implementation](examples/equalizer.py) · [Tests](tests/test_equalizer.py)

Run the five offline tests from the repository root:

```sh
python3 -m unittest discover -s tests -v
```

## Source and upstream projects

This repository contains the two receiver patches and the extracted EQ implementation with tests. The TV adapter, voice deployment, audio feature extractor, and light renderer are described here as parts of my installation.

[Leuchtfeuer](https://git.arianw.de/shrippen/leuchtfeuer) supplies the Invoke firmware. [Shairport Sync](https://github.com/mikebrady/shairport-sync) and [NQPTP](https://github.com/mikebrady/nqptp) provide the AirPlay receiver and timing service. [Home Assistant](https://www.home-assistant.io/) and [Wyoming](https://github.com/rhasspy/wyoming) provide the voice integration. The receiver diffs include the [upstream source notice](patches/UPSTREAM-NOTICE.txt).
