use std::borrow::Cow;

use pyo3::prelude::*;

#[derive(FromPyObject, Default, Clone, Copy)]
pub struct Vector2 {
    x: f32,
    y: f32,
}

impl IntoPy<PyObject> for Vector2 {
    fn into_py(self, py: Python) -> PyObject {
        (self.x, self.y).into_py(py)
    }
}

#[pyclass(get_all)]
#[derive(Default, Clone)]
pub struct Player {
    id: u32,
    radius: f32,
    position: Vec<Vector2>,
}
#[pyclass(get_all)]
#[derive(Default, Clone)]
pub struct Food {
    id: u32,
    radius: f32,
    position: Vector2,
}

#[pyclass(get_all)]
pub struct Replicator {
    players: Vec<Player>,
    foods: Vec<Food>,
}

#[pymethods]
impl Replicator {
    #[new]
    pub fn new() -> Self {
        Self {
            players: Vec::new(),
            foods: Vec::new(),
        }
    }

    pub fn clear(&mut self) {
        self.players.clear();
        self.foods.clear();
    }

    pub fn add_player(&mut self, id: u32, radius: f32, position: Vec<Vector2>) {
        self.players.push(Player {
            id,
            radius,
            position,
        });
    }

    pub fn add_food(&mut self, id: u32, radius: f32, position: Vector2) {
        self.foods.push(Food {
            id,
            radius,
            position,
        });
    }

    pub fn encode(&self) -> Cow<[u8]> {
        let mut buffer = Vec::new();
        for player in &self.players {
            buffer.extend_from_slice(&player.id.to_be_bytes());
            buffer.extend_from_slice(&player.radius.to_be_bytes());
            buffer.extend_from_slice(&((player.position.len() * 2) as u32).to_be_bytes());
            for position in &player.position {
                buffer.extend_from_slice(&position.x.to_be_bytes());
                buffer.extend_from_slice(&position.y.to_be_bytes());
            }
        }

        buffer.extend_from_slice("||||".as_bytes());

        for food in &self.foods {
            buffer.extend_from_slice(&food.id.to_be_bytes());
            buffer.extend_from_slice(&food.radius.to_be_bytes());
            buffer.extend_from_slice(&food.position.x.to_be_bytes());
            buffer.extend_from_slice(&food.position.y.to_be_bytes());
        }
        Cow::Owned(buffer)
    }

    pub fn decode(&mut self, buffer: Vec<u8>) {
        let mut is_player = true;
        let mut player_progress = PlayerProgress::Id;
        let mut food_progress = FoodProgress::Id;
        let mut i = 0;
        let mut length = 0;

        for data in buffer.chunks(4) {
            if data == "||||".as_bytes() {
                is_player = false;
                continue;
            }

            if is_player {
                let players_last = self.players.last_mut();
                match player_progress {
                    PlayerProgress::Id => {
                        self.players.push(Player::default());
                        self.players.last_mut().unwrap().id =
                            u32::from_be_bytes(data.try_into().unwrap());
                        player_progress = PlayerProgress::Radius;
                    }
                    PlayerProgress::Radius => {
                        players_last.unwrap().radius = f32::from_be_bytes(data.try_into().unwrap());
                        player_progress = PlayerProgress::Length;
                    }
                    PlayerProgress::Length => {
                        length = u32::from_be_bytes(data.try_into().unwrap());
                        i = 0;
                        player_progress = PlayerProgress::Bodies;
                    }
                    PlayerProgress::Bodies => {
                        if i % 2 == 0 {
                            let players_last = players_last.unwrap();
                            players_last.position.push(Vector2::default());
                            players_last.position.last_mut().unwrap().x =
                                f32::from_be_bytes(data.try_into().unwrap());
                        } else {
                            players_last.unwrap().position.last_mut().unwrap().y =
                                f32::from_be_bytes(data.try_into().unwrap());
                        }
                        i += 1;
                        if i == length {
                            player_progress = PlayerProgress::Id;
                        }
                    }
                }
            } else {
                let foods_last = self.foods.last_mut();
                match food_progress {
                    FoodProgress::Id => {
                        self.foods.push(Food::default());
                        self.foods.last_mut().unwrap().id =
                            u32::from_be_bytes(data.try_into().unwrap());
                        food_progress = FoodProgress::Radius;
                    }
                    FoodProgress::Radius => {
                        foods_last.unwrap().radius = f32::from_be_bytes(data.try_into().unwrap());
                        food_progress = FoodProgress::X;
                    }
                    FoodProgress::X => {
                        let foods_last = foods_last.unwrap();
                        foods_last.position = Vector2::default();
                        foods_last.position.x = f32::from_be_bytes(data.try_into().unwrap());
                        food_progress = FoodProgress::Y;
                    }
                    FoodProgress::Y => {
                        foods_last.unwrap().position.y =
                            f32::from_be_bytes(data.try_into().unwrap());
                        food_progress = FoodProgress::Id;
                    }
                }
            }
        }
    }
}

enum PlayerProgress {
    Id,
    Radius,
    Length,
    Bodies,
}

enum FoodProgress {
    Id,
    Radius,
    X,
    Y,
}

#[pymodule]
fn Replication(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Replicator>()?;
    m.add_class::<Player>()?;
    m.add_class::<Food>()?;

    m.add("__doc__", "Made in Rust!")?;
    Ok(())
}
