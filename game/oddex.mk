# Original (oddex) species are generated from ../content/ (species, roles, regional dex) and
# their sprite files by ../tools/oddex/gen_species.py. The generated files are committed; this
# rule keeps them fresh when the content, the sprites or the generator change. A stamp stands in for the outputs
# because GNU Make 3.81 (macOS) has no grouped targets.

ODDEX_SPECIES_SRC := $(wildcard ../content/species/*.toml) ../content/roles.toml ../content/regional_dex.toml \
	$(wildcard graphics/pokemon/oddex/*/*.png) ../tools/oddex/gen_species.py ../tools/oddex/species_data.py ../tools/oddex/png_reader.py
ODDEX_SPECIES_STAMP := $(BUILD_DIR)/oddex_species.stamp
ODDEX_SPECIES_OUT := \
	$(INCLUDE_DIRS)/constants/species.h \
	$(INCLUDE_DIRS)/constants/pokedex.h \
	$(INCLUDE_DIRS)/constants/oddex_species.h \
	$(DATA_SRC_SUBDIR)/pokemon/oddex_data.h \
	$(DATA_SRC_SUBDIR)/pokemon/species_info/oddex_families.h

$(ODDEX_SPECIES_STAMP): $(ODDEX_SPECIES_SRC)
	python3 ../tools/oddex/gen_species.py
	@mkdir -p $(@D) && touch $@

$(ODDEX_SPECIES_OUT): $(ODDEX_SPECIES_STAMP) ;

# all_learnables.json already has a recipe (make_learnables.py, which would drop our
# keys), so depend on the stamp from its consumers instead of from the json itself.
$(DATA_SRC_SUBDIR)/pokemon/teachable_learnsets.h: $(ODDEX_SPECIES_STAMP)
$(ALL_TEACHING_TYPES_JSON): $(ODDEX_SPECIES_STAMP)

# Content gates the compiler cannot provide; see ../tools/oddex/check_oddex.sh. Which content
# must already be free of vanilla species is set per scope in ../content/migration_scope.toml.

# Also replays the long route scripts (over 2 minutes each); run before merging content changes.
ODDEX_FULL_SCRIPTS := oddex_title to_littleroot to_starter oddex_gallery oddex_dex to_petalburg to_dolls to_rustboro to_dewford to_mauville to_lavaridge to_norman to_winona to_mossdeep
# Only the scripts no other script includes are run: to_mossdeep includes to_winona ... to_starter
# (oddex_dex and to_dolls include to_littleroot), so its shots cover their baselines too. oddex_title
# stands alone (the title screen, nothing pressed after START).
ODDEX_FULL_RUN := oddex_title oddex_gallery oddex_dex to_dolls to_mossdeep
.PHONY: check-oddex-full
check-oddex-full: rom
	@ODDEX_REGRESSION_SCRIPTS="$(ODDEX_FULL_RUN)" ODDEX_BASELINE_SCRIPTS="$(ODDEX_FULL_SCRIPTS)" bash ../tools/oddex/check_oddex.sh

.PHONY: check-oddex
check-oddex: rom
	@bash ../tools/oddex/check_oddex.sh

# Static map checks only (no ROM build needed); `make check-maps MAPS=LittlerootTown,Route101`.
.PHONY: check-maps
check-maps:
	@python3 ../tools/oddex/check_maps.py $(if $(MAPS),--maps $(MAPS))
