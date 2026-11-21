// Program 7: Promises and async / await

const delay = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms));

function fetchUser(id) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (id > 0) resolve({ id, name: "User" + id });
            else reject(new Error("Invalid user id: " + id));
        }, 100);
    });
}

async function main() {
    // 1. Promise chain with then / catch
    console.log("1. Promise chain");
    await fetchUser(1)
        .then((user) => { console.log("   got", user); return user.id; })
        .then((id) => console.log("   next step with id", id))
        .catch((err) => console.log("   error:", err.message));

    // 2. async / await with try / catch
    console.log("2. async / await");
    try {
        const user = await fetchUser(2);
        console.log("   got", user);
        await fetchUser(-1);                          // this one rejects
    } catch (err) {
        console.log("   caught:", err.message);
    }

    // 3. Promise.all runs promises in parallel
    console.log("3. Promise.all (parallel)");
    const start = Date.now();
    const results = await Promise.all([delay(300, "A"), delay(300, "B"), delay(300, "C")]);
    const took = Date.now() - start;
    console.log("   results:", results, "| finished in about 300 ms:", took < 600);

    // 4. Promise.race: first one to finish wins
    console.log("4. Promise.race");
    const winner = await Promise.race([delay(300, "slow"), delay(100, "fast")]);
    console.log("   winner:", winner);
}

main().then(() => console.log("Done"));
