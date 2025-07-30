use std::collections::HashMap;

use crate::schema::metadata::OptionsMetadata;

use super::OptionsRegistry;

// Replicating https://github.com/juharris/dotnet-OptionsProvider/blob/main/src/OptionsProvider/OptionsProvider/IOptionsProvider.cs
// and https://github.com/juharris/dotnet-OptionsProvider/blob/main/src/OptionsProvider/OptionsProvider/OptionsProviderWithDefaults.cs

// We won't truly use files at runtime, we're just using fake files that are backed by strings because that's easy to use with the `config` library.
pub(crate) type SourceValue = config::File<config::FileSourceString, config::FileFormat>;

pub(crate) type Aliases = HashMap<unicase::UniCase<String>, String>;
pub(crate) type Features = HashMap<String, OptionsMetadata>;
pub(crate) type Sources = HashMap<String, SourceValue>;

pub struct GetOptionsPreferences {
    /// Overrides to apply after the built configuration.
    /// A string is used because it makes it easier to pass to the `config` library, but this may change in the future.
    /// It also makes it simpler and maybe faster to get from other programming languages.
    pub overrides_json: Option<String>,
    pub skip_feature_name_conversion: bool,
}

impl Clone for GetOptionsPreferences {
    fn clone(&self) -> Self {
        Self {
            overrides_json: self.overrides_json.clone(),
            skip_feature_name_conversion: self.skip_feature_name_conversion,
        }
    }
}

impl Default for GetOptionsPreferences {
    fn default() -> Self {
        Self::new()
    }
}

impl GetOptionsPreferences {
    pub fn new() -> Self {
        Self {
            overrides_json: None,
            skip_feature_name_conversion: false,
        }
    }

    pub fn set_overrides_json(&mut self, overrides: Option<String>) {
        self.overrides_json = overrides;
    }

    pub fn set_skip_feature_name_conversion(&mut self, skip_feature_name_conversion: bool) {
        self.skip_feature_name_conversion = skip_feature_name_conversion;
    }
}

pub struct CacheOptions {}

#[doc(hidden)]
#[macro_export]
macro_rules! convert_to_str_slice {
    ($vec:expr) => {
        $vec.iter().map(|s| s.as_str()).collect::<Vec<&str>>()
    };
}

/// ⚠️ Development in progress ⚠️\
/// Not truly considered public and mainly available to support bindings for other languages.
pub struct OptionsProvider {
    aliases: Aliases,
    features: Features,
    sources: Sources,
}

impl OptionsProvider {
    pub(crate) fn new(aliases: &Aliases, features: &Features, sources: &Sources) -> Self {
        OptionsProvider {
            aliases: aliases.clone(),
            features: features.clone(),
            sources: sources.clone(),
        }
    }

    fn _get_entire_config(
        &self,
        feature_names: &[&str],
        cache_options: Option<&CacheOptions>,
        preferences: Option<&GetOptionsPreferences>,
    ) -> Result<Result<config::Config, config::ConfigError>, String> {
        if let Some(_cache_options) = cache_options {
            if let Some(preferences) = preferences {
                if preferences.overrides_json.is_some() {
                    return Err("Caching is not supported yet and caching when overrides are given will not be supported.".to_owned());
                }
            }
            return Err("Caching is not supported yet.".to_owned());
        };
        let mut config_builder = config::Config::builder();
        let mut skip_feature_name_conversion = false;
        if let Some(_preferences) = preferences {
            skip_feature_name_conversion = _preferences.skip_feature_name_conversion;
        }
        for feature_name in feature_names {
            // Check for an alias.
            // Canonical feature names are also included as keys in the aliases map.
            let canonical_feature_name = if skip_feature_name_conversion {
                &feature_name.to_string()
            } else {
                &self.get_canonical_feature_name(feature_name)?
            };

            let source = match self.sources.get(canonical_feature_name) {
                Some(src) => src,
                // Should not happen.
                // All canonical feature names are included as keys in the sources map.
                // It could happen in the future if we allow aliases to be added directly, but we should try to validate them when the provider is built.
                None => {
                    return Err(format!(
                        "Feature name {:?} was not found.",
                        canonical_feature_name
                    ))
                }
            };
            config_builder = config_builder.add_source(source.clone());
        }
        if let Some(preferences) = preferences {
            if let Some(overrides) = &preferences.overrides_json {
                config_builder = config_builder
                    .add_source(config::File::from_str(overrides, config::FileFormat::Json));
            }
        }

        Ok(config_builder.build())
    }
}

impl OptionsRegistry for OptionsProvider {
    fn get_all_options(
        &self,
        feature_names: &[&str],
        cache_options: Option<&CacheOptions>,
        preferences: Option<&GetOptionsPreferences>,
    ) -> Result<serde_json::Value, String> {
        let config = self._get_entire_config(feature_names, cache_options, preferences)?;

        match config {
            Ok(cfg) => match cfg.try_deserialize() {
                Ok(value) => Ok(value),
                Err(e) => Err(e.to_string()),
            },
            Err(e) => Err(e.to_string()),
        }
    }

    // Map an alias or canonical feature name (perhaps derived from a file name) to a canonical feature name.
    // Canonical feature names map to themselves.
    //
    // @param feature_name The name of an alias or a feature.
    // @return The canonical feature name.
    fn get_canonical_feature_name(&self, feature_name: &str) -> Result<String, String> {
        // Canonical feature names are also included as keys in the aliases map.
        let feature_name = unicase::UniCase::new(feature_name.to_owned());
        match self.aliases.get(&feature_name) {
            Some(canonical_name) => Ok(canonical_name.to_owned()),
            None => Err(format!(
                "The given feature {:?} was not found.",
                feature_name
            )),
        }
    }

    fn get_canonical_feature_names(&self, feature_names: &[&str]) -> Result<Vec<String>, String> {
        feature_names
            .iter()
            .map(|name| self.get_canonical_feature_name(name))
            .collect()
    }

    fn get_feature_metadata(&self, canonical_feature_name: &str) -> Option<OptionsMetadata> {
        self.features.get(canonical_feature_name).cloned()
    }

    fn get_features(&self) -> Vec<String> {
        self.sources.keys().cloned().collect()
    }

    fn get_features_with_metadata(&self) -> Features {
        self.features.clone()
    }

    fn get_options(&self, key: &str, feature_names: &[&str]) -> Result<serde_json::Value, String> {
        self.get_options_with_preferences(key, feature_names, None, None)
    }

    fn get_options_with_preferences(
        &self,
        key: &str,
        feature_names: &[&str],
        cache_options: Option<&CacheOptions>,
        preferences: Option<&GetOptionsPreferences>,
    ) -> Result<serde_json::Value, String> {
        let config = self._get_entire_config(feature_names, cache_options, preferences)?;

        match config {
            Ok(cfg) => match cfg.get(key) {
                Ok(value) => Ok(value),
                Err(e) => Err(e.to_string()),
            },
            Err(e) => Err(e.to_string()),
        }
    }
}
