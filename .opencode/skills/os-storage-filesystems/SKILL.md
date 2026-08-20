---
name: os-storage-filesystems
description: Applies the persistence half of OSTEP (Operating Systems: Three Easy Pieces) to understand and debug storage: disks and SSDs, filesystem data structures and the inode model, crash consistency with journaling and copy-on-write, and how filesystems use the block layer. Use when the user says 'how does a filesystem work', 'inode', 'journaling', 'ext4', 'xfs', 'crash consistency', 'block layer', 'RAID', 'filesystem design', 'OSTEP persistence', 'why did my file get corrupted', or when reasoning about data on disk.
---

# Operating Systems: Three Easy Pieces — Storage and Filesystems

The persistence half of OSTEP turns storage from a black box into a model: disks with a block interface, a filesystem built on inodes and data blocks, and crash consistency as the discipline that keeps the tree intact after a power loss. This skill encodes the model so storage behavior is explained, designed, and debugged correctly.

## Disks and SSDs
- A disk is a device of fixed-size blocks; reads and writes happen at block granularity, and the cost depends on where the data lives on the platter.
- Mechanical disks pay a seek and rotation cost per random access, so sequential access is dramatically cheaper than random.
- SSDs have no seek, but write endurance and write amplification still favor batching and aligned writes.
- The OS papers over the device with a block layer so filesystems see a simple set of read/write primitives.

## Filesystem Data Structures
- A filesystem divides the disk into regions: a superblock describing the layout, inode bitmaps, data bitmaps, inode tables, and data blocks.
- An inode is the per-file metadata (owner, size, timestamps, block pointers) that names the data blocks of a file.
- Multi-level indexing (direct, indirect, double-indirect pointers) lets a file grow beyond the blocks an inode can name directly.
- Directories are files whose data maps names to inode numbers, which is why a directory entry is just a name-to-inode pair.

## Crash Consistency and Journaling
- A crash mid-operation can leave the filesystem torn: an inode pointing at data that was never written, or a bitmap that disagrees with reality.
- Journaling solves this by writing the operation's metadata changes to a log first, then applying them, so a crash replays the log to a consistent state.
- The ordering discipline — write the data block before committing the journal entry — is what guarantees no torn metadata.
- Without journaling, a full consistency check must rebuild the state from a scan of every block; journaling makes recovery fast and bounded.

## Copy-on-Write and Modern Designs
- Copy-on-write filesystems (like the Btrfs and ZFS model) never overwrite in place; they write new blocks and repoint the tree, which keeps the structure consistent by construction.
- COW gives snapshots almost for free: the old tree is still intact, so a snapshot is a pointer, not a copy.
- Filesystem choices are trade-offs: journaling favors simplicity and wide compatibility, COW favors snapshots, checksums, and self-healing.
- Match the filesystem to the workload — logs and databases prefer ordered durability, while bulk media prefers throughput with laxer sync guarantees.

## Pairs with
operating-systems-three-easy-pieces, database-internals-engines, linux-programming-interface, systems-performance-profiling, high-performance-mysql
