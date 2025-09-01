use std::sync::{Arc, Mutex};

use pyo3::{
    create_exception,
    exceptions::{PyException, PyIOError, PyTypeError, PyValueError},
    prelude::*,
    types::PyCFunction,
};
use pythonize::pythonize;
use tokio::task::spawn_blocking;
use tracing::{debug, instrument, level_filters::LevelFilter, trace_span};
use tracing_subscriber::{EnvFilter, fmt::format::FmtSpan};

#[pyclass]
struct Script(Arc<Mutex<Option<rcu::Script>>>);

#[pymethods]
impl Script {
    #[new]
    #[pyo3(signature = (name="example", description="", server="ws://localhost:37265/"))]
    fn new(name: &str, description: &str, server: &str) -> Self {
        let script = rcu::Script::new(name)
            .description(description)
            .server(server);
        Self(Arc::new(Mutex::new(Some(script))))
    }

    fn on_init<'a>(&mut self, py: Python<'a>) -> PyResult<Bound<'a, PyCFunction>> {
        callback_registerer(self.0.clone(), py, |script, callback| {
            script.on_init(async move |ctx| {
                let _ = trace_span!("on_init").enter();
                spawn_blocking(move || {
                    Python::attach(|py| {
                        callback.call1(py, (Context(ctx),)).unwrap();
                    })
                })
                .await
                .unwrap();
                Ok(())
            })
        })
    }

    fn on_execute<'a>(&mut self, py: Python<'a>) -> PyResult<Bound<'a, PyCFunction>> {
        callback_registerer(self.0.clone(), py, |script, callback| {
            script.on_execute(move |ctx, args| {
                let _ = trace_span!("on_execute").enter();
                let callback = Python::attach(|py| callback.clone_ref(py));
                async move {
                    Ok(spawn_blocking(move || {
                        Python::attach(|py| {
                            callback
                                .call1(py, (Context(ctx), pythonize(py, &args).unwrap()))
                                .unwrap()
                                .extract(py)
                                .unwrap()
                        })
                    })
                    .await
                    .unwrap())
                }
            })
        })
    }

    #[pyo3(signature = (logger=false))]
    fn run(&mut self, py: Python<'_>, logger: bool) -> PyResult<()> {
        py.detach(|| {
            let Some(script) = ({ self.0.lock().unwrap().take() }) else {
                return Err(PyValueError::new_err(
                    "script is either already running or stopped",
                ));
            };
            if logger {
                tracing_subscriber::fmt()
                    .with_span_events(FmtSpan::CLOSE)
                    .with_env_filter(
                        EnvFilter::from_default_env().add_directive(LevelFilter::INFO.into()),
                    )
                    .init();
            }

            debug!("Creating tokio runtime");
            let rt = tokio::runtime::Builder::new_multi_thread()
                .enable_all()
                .build()
                .unwrap();
            rt.block_on(script.run()).unwrap();

            Ok(())
        })
    }
}

fn callback_registerer<F>(
    script: Arc<Mutex<Option<rcu::Script>>>,
    py: Python<'_>,
    f: F,
) -> PyResult<Bound<'_, PyCFunction>>
where
    F: Fn(rcu::Script, Py<PyAny>) -> rcu::Script + Clone + Send + Sync + 'static,
{
    PyCFunction::new_closure(py, None, None, move |args, _kw| -> PyResult<()> {
        let callback = args.get_item(0)?;
        if !callback.is_callable() {
            return Err(PyTypeError::new_err("callback is not callable"));
        }
        let callback = callback.unbind();
        let f = f.clone();
        args.py().detach(|| {
            let mut lock = script.lock().unwrap();
            *lock = lock.take().map(|script| f(script, callback));
        });
        Ok(())
    })
}

#[pyclass]
struct Context(rcu::Context);

#[pymethods]
impl Context {
    #[instrument(level = "trace", skip_all)]
    fn query_gametime(&mut self) -> Result<i64, RcuError> {
        Ok(tokio::runtime::Handle::current().block_on(self.0.query_gametime())?)
    }

    #[instrument(level = "trace", skip_all)]
    fn info(&mut self, message: &str) -> Result<(), RcuError> {
        tokio::runtime::Handle::current().block_on(self.0.info(message))?;
        Ok(())
    }
}

struct RcuError(rcu::Error);

impl From<RcuError> for PyErr {
    fn from(value: RcuError) -> Self {
        match value.0 {
            rcu::Error::ErrorCode(code) => ApiError::new_err((code as i32, code.to_string())),
            _ => PyIOError::new_err(value.0.to_string()),
        }
    }
}

impl From<rcu::Error> for RcuError {
    fn from(value: rcu::Error) -> Self {
        Self(value)
    }
}

create_exception!(module, ApiError, PyException);

#[pymodule]
mod rcu_shim {
    #[pymodule_export]
    use super::{ApiError, Context, Script};
}
