use nzb_rs::Segment as RustSegment;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::fmt::{Debug, Display};

// Python wrapper class for RustSegment
#[pyclass(module = "rnzb", frozen, eq, hash)]
#[derive(Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Segment {
    #[pyo3(get)]
    pub size: u32,
    #[pyo3(get)]
    pub number: u32,
    #[pyo3(get)]
    pub message_id: String,
}

// Implement Python-esque debug
impl Debug for Segment {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Segment(size={}, number={}, message_id={:?})",
            self.size, self.number, self.message_id
        )
    }
}

// Implement Python-esque display
// It's identical to Debug
impl Display for Segment {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        Debug::fmt(&self, f)
    }
}

// Implement conversion from RustSegment to Segment
impl From<RustSegment> for Segment {
    fn from(s: RustSegment) -> Self {
        Self {
            size: s.size,
            number: s.number,
            message_id: s.message_id.clone(),
        }
    }
}

// Implement conversion from Segment to RustSegment
impl From<Segment> for RustSegment {
    fn from(s: Segment) -> Self {
        Self {
            size: s.size,
            number: s.number,
            message_id: s.message_id,
        }
    }
}

#[pymethods]
impl Segment {
    #[new]
    #[pyo3(signature = (*, size, number, message_id))]
    pub fn __new__(size: u32, number: u32, message_id: String) -> Self {
        Self {
            size,
            number,
            message_id,
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
