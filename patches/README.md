# Receiver changes

These two diffs target the RTSP handler in [Shairport Sync 5.6.3](https://github.com/mikebrady/shairport-sync/releases/tag/5.6.3). Both were present in the receiver build used on all three Invokes.

| Patch | Behavior | Hardware check |
| --- | --- | --- |
| [Event listener cleanup](event-listener-cleanup.patch) | Closes the listening socket after the event worker has been joined, including cancellation while waiting in accept. | Repeated initial control sessions and disconnected before opening the event channel. The receiver reused one port for all 36 sessions. |
| [Combined capability response](combined-info.patch) | Adds the ordinary receiver info dictionary to a successful initial control setup when the sender sets the boolean request flag. | Compared the combined response with ordinary GET /info and checked the lossless capability. False, missing, and invalid request flags retained the ordinary setup behavior. |

## Check against the release source

From the root of this repository, run the following with Git. It downloads the pinned release into a temporary directory, applies both changes in that checkout, and prints the resulting diff. It requires network access and doesn't contact a speaker.

```sh
(
  set -eu
  patches="$PWD/patches"
  checkout=$(mktemp -d)
  git clone --quiet --depth 1 --branch 5.6.3 https://github.com/mikebrady/shairport-sync.git "$checkout"
  git -C "$checkout" apply "$patches/event-listener-cleanup.patch"
  git -C "$checkout" apply "$patches/combined-info.patch"
  git -C "$checkout" diff -- rtsp.c
)
```

Applying the patches checks source compatibility. The session and listening results above came from the deployed ARM receiver. Building an Invoke receiver also requires its target libraries, audio configuration, and timing service.
