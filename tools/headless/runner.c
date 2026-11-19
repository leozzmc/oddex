#include <mgba/flags.h>
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <mgba/core/serialize.h>
#include <mgba-util/png-io.h>
#include <mgba-util/vfs.h>

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

static struct mCore* core;
static color_t* video;
static unsigned width, height;
static unsigned long frame;

static const char* keyNames[] = { "A", "B", "SELECT", "START", "RIGHT", "LEFT", "UP", "DOWN", "R", "L" };

static uint32_t parseKeys(const char* spec) {
	uint32_t keys = 0;
	char buf[128];
	snprintf(buf, sizeof(buf), "%s", spec);
	for (char* tok = strtok(buf, "+,"); tok; tok = strtok(NULL, "+,")) {
		int found = 0;
		for (size_t i = 0; i < sizeof(keyNames) / sizeof(*keyNames); ++i) {
			if (strcasecmp(tok, keyNames[i]) == 0) {
				keys |= 1u << i;
				found = 1;
			}
		}
		if (!found) {
			fprintf(stderr, "unknown key: %s\n", tok);
			exit(2);
		}
	}
	return keys;
}

// ODDEX_RESET_WATCH names a u32 the game only ever increments (gMain.vblankCounter1); it
// drops back to 0 only when the game resets, which shows no crash screen.
static uint32_t resetWatch;
static uint32_t lastCounter;

static void checkReset(void) {
	if (!resetWatch) {
		return;
	}
	uint32_t counter = core->busRead32(core, resetWatch);
	// Boot clears and re-inits the counter around frame 13, so only watch once it has settled.
	if (counter < lastCounter && frame > 60) {
		fprintf(stderr, "ODDEX_RESET game reset at frame %lu (counter %u -> %u)\n", frame, lastCounter, counter);
	}
	lastCounter = counter;
}

static void run(uint32_t keys, unsigned long frames) {
	core->setKeys(core, keys);
	for (unsigned long i = 0; i < frames; ++i) {
		core->runFrame(core);
		++frame;
		checkReset();
	}
	core->setKeys(core, 0);
}

static void makeParents(const char* path) {
	char buf[512];
	snprintf(buf, sizeof(buf), "%s", path);
	for (char* p = buf + 1; *p; ++p) {
		if (*p == '/') {
			*p = '\0';
			mkdir(buf, 0755);
			*p = '/';
		}
	}
}

static void screenshot(const char* path) {
	makeParents(path);
	struct VFile* vf = VFileOpen(path, O_CREAT | O_TRUNC | O_WRONLY);
	if (!vf) {
		fprintf(stderr, "cannot write %s\n", path);
		exit(1);
	}
	png_structp png = PNGWriteOpen(vf);
	png_infop info = PNGWriteHeader(png, width, height);
	PNGWritePixels(png, width, height, width, video);
	PNGWriteClose(png, info);
	vf->close(vf);
	printf("[frame %lu] shot %s\n", frame, path);
}

static void stateIo(const char* path, int save) {
	if (save) {
		makeParents(path);
	}
	struct VFile* vf = VFileOpen(path, save ? (O_CREAT | O_TRUNC | O_WRONLY) : O_RDONLY);
	if (!vf || !(save ? mCoreSaveStateNamed(core, vf, SAVESTATE_ALL) : mCoreLoadStateNamed(core, vf, SAVESTATE_ALL))) {
		fprintf(stderr, "%s state failed: %s\n", save ? "save" : "load", path);
		exit(1);
	}
	if (!save && resetWatch) {
		lastCounter = core->busRead32(core, resetWatch);
	}
	vf->close(vf);
	printf("[frame %lu] %s %s\n", frame, save ? "saved" : "loaded", path);
}

static void runScript(const char* path, int depth);

static void execute(char* line, int lineno, const char* dir, int depth) {
	char* argv[8];
	int argc = 0;
	for (char* tok = strtok(line, " \t\r\n"); tok && argc < 8; tok = strtok(NULL, " \t\r\n")) {
		if (tok[0] == '#') {
			break;
		}
		argv[argc++] = tok;
	}
	if (!argc) {
		return;
	}
	const char* cmd = argv[0];
	if (!strcmp(cmd, "repeat") && argc >= 3) {
		long n = atol(argv[1]);
		char rest[256] = "";
		for (int i = 2; i < argc; ++i) {
			strcat(rest, argv[i]);
			strcat(rest, " ");
		}
		for (long i = 0; i < n; ++i) {
			char copy[256];
			strcpy(copy, rest);
			execute(copy, lineno, dir, depth);
		}
	} else if (!strcmp(cmd, "wait") && argc == 2) {
		run(0, atol(argv[1]));
	} else if (!strcmp(cmd, "press") && argc >= 2) {
		run(parseKeys(argv[1]), argc > 2 ? atol(argv[2]) : 2);
		run(0, argc > 3 ? atol(argv[3]) : 10);
	} else if (!strcmp(cmd, "hold") && argc == 3) {
		run(parseKeys(argv[1]), atol(argv[2]));
	} else if (!strcmp(cmd, "shot") && argc == 2) {
		screenshot(argv[1]);
	} else if (!strcmp(cmd, "save") && argc == 2) {
		stateIo(argv[1], 1);
	} else if (!strcmp(cmd, "load") && argc == 2) {
		stateIo(argv[1], 0);
	} else if (!strcmp(cmd, "include") && argc == 2) {
		char path[512];
		if (argv[1][0] == '/') {
			snprintf(path, sizeof(path), "%s", argv[1]);
		} else {
			snprintf(path, sizeof(path), "%s/%s", dir, argv[1]);
		}
		runScript(path, depth + 1);
	} else {
		fprintf(stderr, "line %d: bad command: %s\n", lineno, cmd);
		exit(2);
	}
}

static void quietLog(struct mLogger* logger, int category, enum mLogLevel level, const char* format, va_list args) {
	(void) logger;
	(void) category;
	if (level & (mLOG_FATAL | mLOG_ERROR)) {
		vfprintf(stderr, format, args);
		fputc('\n', stderr);
	}
}

static struct mLogger logger = { .log = quietLog };

static void runScript(const char* path, int depth) {
	if (depth > 8) {
		fprintf(stderr, "include nested too deeply: %s\n", path);
		exit(2);
	}
	FILE* script = fopen(path, "r");
	if (!script) {
		fprintf(stderr, "cannot open %s\n", path);
		exit(1);
	}
	char dir[512];
	snprintf(dir, sizeof(dir), "%s", path);
	char* slash = strrchr(dir, '/');
	if (slash) {
		*slash = '\0';
	} else {
		strcpy(dir, ".");
	}
	char line[256];
	int lineno = 0;
	while (fgets(line, sizeof(line), script)) {
		execute(line, ++lineno, dir, depth);
	}
	fclose(script);
}

int main(int argc, char** argv) {
	if (argc != 3) {
		fprintf(stderr, "usage: %s ROM SCRIPT\n", argv[0]);
		return 2;
	}
	mLogSetDefaultLogger(&logger);
	core = mCoreFind(argv[1]);
	if (!core || !core->init(core)) {
		fprintf(stderr, "cannot open core for %s\n", argv[1]);
		return 1;
	}
	mCoreInitConfig(core, NULL);
	core->desiredVideoDimensions(core, &width, &height);
	video = calloc(width * height, BYTES_PER_PIXEL);
	core->setVideoBuffer(core, video, width);
	// Wall-clock RTC feeds the game's RNG, so pin it to make runs reproducible.
	core->rtc.override = RTC_FAKE_EPOCH;
	core->rtc.value = 1767268800000LL; // 2026-01-01T12:00:00Z, daytime
	if (!mCoreLoadFile(core, argv[1])) {
		fprintf(stderr, "cannot load %s\n", argv[1]);
		return 1;
	}
	core->reset(core);
	const char* watch = getenv("ODDEX_RESET_WATCH");
	if (watch && *watch) {
		resetWatch = (uint32_t) strtoul(watch, NULL, 0);
	}

	runScript(argv[2], 0);
	printf("done at frame %lu\n", frame);

	mCoreConfigDeinit(&core->config);
	core->deinit(core);
	free(video);
	return 0;
}
