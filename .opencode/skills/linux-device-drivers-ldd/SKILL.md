---
name: linux-device-drivers-ldd
description: "Writes Linux kernel drivers: modules, char/block devices, interrupts, and concurrency. Use when the user says 'kernel module', 'device driver', 'char device', 'insmod', 'interrupt handler', 'DMA', 'sysfs', 'LDD', 'Corbet Rubini', or when hardware must meet Linux."
---

# Linux Device Drivers (LDD)

Distilled from Corbet/Rubini/Kroah-Hartman *Linux Device Drivers*: drivers
are kernel citizens — same rules as core kernel code (no libc, sleep
discipline, locking everywhere), plus the device model that makes hardware
discoverable and manageable.

## Purpose

Ship correct, upstreamable drivers: loadable modules exposing hardware
through the right subsystem with proper locking, memory handling, and
userspace interfaces.

## The practice (in driver-authoring order)

1. **Module skeleton, done right.** init/exit, `module_init/exit`,
   MODULE_LICENSE (tainting matters for supportability), parameters via
   `module_param` (typed, permissioned). Load/unload cycles clean every
   time — rmmod must undo everything insmod did, or the bug is yours.
2. **Char devices first.** cdev registration, file_operations (open/release/
   read/write/llseek/ioctl-unlocked), user/kernel boundary discipline:
   `copy_to/from_user` checked ALWAYS (unverified user pointers are CVEs),
   no sleeping while atomic, no kernel addresses leaked to userspace.
3. **Concurrency from day one.** Open file descriptions shared across
   processes/threads: mutexes vs spinlocks (sleep allowed? interrupt
   context?), lock ordering documented, per-device data (never globals).
   Assume SMP + preemption + interrupts from the first line.
4. **Interrupts and timing.** Request/free IRQs with shared-line discipline;
   top half minimal (acknowledge, schedule), bottom halves via tasklets/
   workqueues/threaded IRQs; no sleeping in interrupt context, ever.
   Time handling with jiffies/ktime appropriate to the precision needed.
5. **Memory and DMA.** kmalloc vs vmalloc vs DMA-coherent (consistent) vs
   streaming mappings — each with its cache-coherency contract; mmap for
   zero-copy userspace access with VMA ops correct; I/O memory via
   ioremap (never raw dereference of device addresses).
6. **Device model integration.** bus/device/driver binding, sysfs attributes
   (one value per file, staged show/store), udev rules for naming, device
   tree/ACPI for non-discoverable hardware. Userspace interface stable and
   documented — breaking it breaks the world.

## Verification

Driver ships with: lockdep clean, sparse/smatch clean, fault-injection
survived (open/write/ioctl error paths), unload/reload cycle proof, and a
test exercising every file_operation including error returns. Untested error
paths are untested code, full stop.

## Pairs with

- `linux-kernel-development` (kernel fundamentals),
  `linux-kernel-memory-management`/`linux-kernel-scheduler` (subsystems),
  `concurrent-lock-free-structures` (locking depth),
  `alephone-binary-exploitation` (what user-pointer bugs cost).
