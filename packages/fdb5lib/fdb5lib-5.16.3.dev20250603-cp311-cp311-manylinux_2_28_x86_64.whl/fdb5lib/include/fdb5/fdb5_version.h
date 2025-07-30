#ifndef fdb5_fdb5_version_h
#define fdb5_fdb5_version_h

#define fdb5_VERSION_STR "5.16.3.dev20250603"
#define fdb5_VERSION     "5.16.3"

#define fdb5_VERSION_MAJOR 5
#define fdb5_VERSION_MINOR 16
#define fdb5_VERSION_PATCH 3

#ifdef __cplusplus
extern "C" {
#endif

const char * fdb5_version();

unsigned int fdb5_version_int();

const char * fdb5_version_str();

const char * fdb5_git_sha1();

#ifdef __cplusplus
}
#endif

#endif
