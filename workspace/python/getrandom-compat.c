/* Rust std uses a weak libc getrandom reference. The captured libc exposes an
 * ENOSYS stub versioned GLIBC_2.25. Resolve that reference inside this module
 * through the Linux syscall, preserving errno and Rust's own error handling.
 * Linux 4.9 supports this syscall; no entropy substitution is performed.
 */
#define _GNU_SOURCE
#include <sys/syscall.h>
#include <unistd.h>

__attribute__((visibility("hidden")))
ssize_t __wrap_getrandom(void *buffer, size_t length, unsigned int flags)
{
    return syscall(SYS_getrandom, buffer, length, flags);
}
