# Original (oddex) species are generated from ../content/species/*.toml and ../content/roles.toml by
# ../tools/oddex/gen_species.py. The generated files are committed; this rule keeps them
# fresh when the content or the generator changes. A stamp stands in for the outputs
# because GNU Make 3.81 (macOS) has no grouped targets.

ODDEX_SPECIES_SRC := $(wildcard ../content/species/*.toml) ../content/roles.toml ../content/regional_dex.toml ../tools/oddex/gen_species.py ../tools/oddex/species_data.py
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

# Content gates the compiler cannot provide; see ../tools/oddex/check_oddex.sh.
# ODDEX_STRICT_MAPS lists the maps that must already be free of vanilla species; grow it as
# plan B migrates each route.
ODDEX_STRICT_MAPS ?=
export ODDEX_STRICT_MAPS

.PHONY: check-oddex
check-oddex: rom
	@bash ../tools/oddex/check_oddex.sh
