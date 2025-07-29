use pyo3::prelude::*;
use pyo3::types::PyTuple;
use serde::{Deserialize, Serialize};
use std::fmt::{self, Debug, Display, Formatter};

// Wrapper around a Vec<T> to implement IntoPyObject for Python tuple.
#[derive(Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(transparent)]
pub struct Tuple<T>(pub Vec<T>);

impl<'py, T: IntoPyObject<'py>> IntoPyObject<'py> for Tuple<T> {
    type Target = PyTuple;
    type Output = Bound<'py, Self::Target>;
    type Error = std::convert::Infallible;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Ok(PyTuple::new(py, self.0).unwrap())
    }
}

// Implement Vec<T> to Tuple<T> conversion.
impl<T> From<Vec<T>> for Tuple<T> {
    fn from(v: Vec<T>) -> Self {
        Self(v)
    }
}

// Implement python-esque Debug
impl<T: Debug> Debug for Tuple<T> {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        // Handle empty tuple
        if self.0.is_empty() {
            return write!(f, "()");
        }

        // Handle single element tuple (with trailing comma)
        if self.0.len() == 1 {
            return write!(f, "({:?},)", self.0[0]);
        }

        // Handle multiple elements
        write!(
            f,
            "({})",
            self.0
                .iter()
                .map(|x| format!("{:?}", x))
                .collect::<Vec<_>>()
                .join(", ")
        )
    }
}

// Implement Python-esque Display
impl<T: Debug> Display for Tuple<T> {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        Debug::fmt(&self, f)
    }
}
