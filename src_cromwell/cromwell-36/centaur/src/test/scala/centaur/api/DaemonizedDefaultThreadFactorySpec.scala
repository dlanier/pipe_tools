package centaur.api

import org.scalatest.{FlatSpec, Matchers}

class DaemonizedDefaultThreadFactorySpec extends FlatSpec with Matchers {

  behavior of "DaemonizedDefaultThreadFactory"

  it should "create a non-blocking execution context" in {
    val thread = DaemonizedDefaultThreadFactory.newThread(() => {})
    thread.getName should startWith("daemonpool-thread-")
    thread.isDaemon should be(true)
  }

}
