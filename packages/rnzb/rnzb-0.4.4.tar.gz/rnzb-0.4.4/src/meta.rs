use crate::tuple::Tuple;
use nzb_rs::Meta as RustMeta;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::fmt::{Debug, Display};

// Python wrapper class for Meta
#[pyclass(module = "rnzb", frozen, eq, hash)]
#[derive(Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Meta {
    #[pyo3(get)]
    pub title: Option<String>,
    #[pyo3(get)]
    pub passwords: Tuple<String>,
    #[pyo3(get)]
    pub tags: Tuple<String>,
    #[pyo3(get)]
    pub category: Option<String>,
}

// Implement Python-esque debug
impl Debug for Meta {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Meta(title={}, passwords={}, tags={}, category={})",
            self.title
                .as_ref()
                .map_or_else(|| "None".to_string(), |t| format!("{:?}", t)),
            self.passwords,
            self.tags,
            self.category
                .as_ref()
                .map_or_else(|| "None".to_string(), |t| format!("{:?}", t)),
        )
    }
}

// Implement Python-esque display
// It's identical to Debug
impl Display for Meta {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        Debug::fmt(&self, f)
    }
}

// Implement conversion from RustMeta to Meta
impl From<RustMeta> for Meta {
    fn from(m: RustMeta) -> Self {
        Self {
            title: m.title.clone(),
            passwords: m.passwords.clone().into(),
            tags: m.tags.clone().into(),
            category: m.category.clone(),
        }
    }
}

// Implement conversion from Meta to RustMeta
impl From<Meta> for RustMeta {
    fn from(m: Meta) -> Self {
        RustMeta {
            title: m.title.clone(),
            passwords: m.passwords.0.clone(),
            tags: m.tags.0.clone(),
            category: m.category.clone(),
        }
    }
}

#[pymethods]
impl Meta {
    #[new]
    #[pyo3(signature = (*, title=None, passwords=Vec::new(), tags=Vec::new(), category=None))]
    pub fn __new__(
        title: Option<String>,
        passwords: Vec<String>,
        tags: Vec<String>,
        category: Option<String>,
    ) -> Self {
        Self {
            title,
            passwords: passwords.into(),
            tags: tags.into(),
            category,
        }
    }
    pub fn __repr__(&self) -> String {
        format!("{:?}", self)
    }

    pub fn __str__(&self) -> String {
        self.__repr__()
    }

    pub fn __copy__(&self) -> Self {
        self.clone()
    }
}
